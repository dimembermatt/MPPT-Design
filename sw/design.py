"""_summary_
@file       design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate parameters of a DC-DC boost converter.

            We want to determine the following:
            - switching frequency
            - switch sizing (v_ds_max, i_ds_max, FOM, r_ds_on, c_oss)
            - capacitor sizing (capacitance)
            - inductor sizing (inductance)

            To do this we, optimize for the following
            - minimize power loss (and sizing requirements) for switches
                - r_ds_on affects conduction loss, is (nearly) constant
                - c_oss affects switching loss, is linear w/ frequency
                    - want to minimise FOM with a focus on minimizing c_oss
                    - a smaller c_oss allows us to get a higher freq across loads within
                    the power budget
                - want to be able to maximize frequency for all loads (e.g. input/output)
            - minimize sizing requirements for passives
                - inductance and capacitance depends on the switching frequency.
                - a higher switching frequency that is within our power budget minimizes
                size.

            - A secondary priority is put on component cost, package, and footprint.

            We can derive that the second optimization target is subservient to the
            first; we MUST derive the switch sizing first.

@version    0.1.0
@date       2023-03-02
"""

import argparse
import sys

import matplotlib.pyplot as plt
from design_procedures.nonideal_model import model_nonideal_cell
from design_procedures.passives_design import (get_inductor_core_loss,
                                               get_inductor_sizing,
                                               get_passive_sizing)
from design_procedures.switch_design import (get_switch_duty_cycle_map,
                                             get_switch_op_fs,
                                             get_switch_op_fs_map,
                                             get_switch_requirements)
from design_procedures.thermal_design import get_switch_thermals

SKIP_FOM_SEARCH = True
SKIP_THERMAL_SEARCH = False

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    plt.ion()

    # Cell characteristics
    v_oc = 0.721
    i_sc = 6.15
    v_mpp = 0.621
    i_mpp = 5.84

    # Array characteristics
    num_cells = 111
    # Note that we get divide by 0 errors should the lower bounds be 0% or 100%
    # of the array voltage. DON'T DO IT!
    # only run input at top 75% of VIN candidates less than VMPP, and top 75% of
    # VIN candidates greater than VMPP
    le_top_pct = 0.705
    ue_top_pct = 0.5 # We don't care as much about top side loss since MPP will generally always be left and a better op.
    v_in_range = [
        num_cells * v_mpp * (1 - le_top_pct),  # V_IN_LOW
        num_cells * v_mpp,  # V_IN_MPP
        num_cells * v_mpp + ((v_oc - v_mpp) * ue_top_pct * num_cells),  # V_IN_HIGH
    ]
    p_in_range = [
        v_in_range[0] * model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[0] / num_cells),
        v_in_range[1] * model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[1] / num_cells),
        v_in_range[2] * model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[2] / num_cells)
    ]

    i_in_range = [0, i_mpp, i_sc]  # I_IN_LOW  # I_IN_MPP  # I_IN_HIGH
    r_ci_v = v_in_range[2] / 100  # V
    r_ci = r_ci_v / v_in_range[2] / 2

    # Battery characteristics
    v_out_range = [85, 105, 125]  # V_OUT_LOW  # V_OUT_MID  # V_OUT_HIGH
    r_co_v = 0.250  # V
    r_co = r_co_v / v_out_range[2] / 2

    # Converter characteristics
    r_l_a = 2.75  # A
    r_l = r_l_a / i_in_range[2] / 2
    sf = 1.25

    # Efficiency and distribution of losses
    eff = 0.97
    p_transfer = v_in_range[1] * i_in_range[1]
    p_loss = p_transfer * (1 - eff)
    sw_1_p_dist = 0.29
    sw_2_p_dist = sw_1_p_dist
    ci_p_dist = 0.005
    co_p_dist = 0.03
    l_p_dist = 1 - sw_1_p_dist - sw_2_p_dist - ci_p_dist - co_p_dist

    # Step 0. Print out the specified design parameters.
    print(f"----------------------------------------")
    print(f"STEP 0")
    print(f"User design criteria:")

    print(f"Input Array:")
    print(f"    [{v_in_range[0] :.3f}, {v_in_range[1] :.3f}, {v_in_range[2] :.3f}] V")
    print(f"    [{p_in_range[0] :.3f}, {p_in_range[1] :.3f}, {p_in_range[2] :.3f}] W")
    print(f"    [{i_in_range[0] :.3f}, {i_in_range[1] :.3f}, {i_in_range[2] :.3f}] A")
    print(f"Output Battery:")
    print(
        f"    [{v_out_range[0] :.3f}, {v_out_range[1] :.3f}, {v_out_range[2] :.3f}] V"
    )

    print(f"Target Ripple:")
    print(f"    R_CI - {r_ci_v :.3f} V [{r_ci*100 :.3f} %]")
    print(f"    R_CO - {r_co_v :.3f} V [{r_co*100 :.3f} %]")
    print(f"    R_L - {r_l_a :.3f} A [{r_l*100 :.3f} %]")
    print(f"Safety Factor: {sf :.3f}")

    print(f"Target Converter Efficiency: {eff :.3f}")
    print(f"    Target Power Loss Budget {p_loss :.3f} W")
    print(f"Power Loss Allocation:")
    print(f"    SW1 - {sw_1_p_dist :.3f} ({p_loss * sw_1_p_dist :.3f} W)")
    print(f"    SW1 - {sw_2_p_dist :.3f} ({p_loss * sw_2_p_dist :.3f} W)")
    print(f"    C_I - {ci_p_dist :.3f} ({p_loss * ci_p_dist :.3f} W)")
    print(f"    C_O - {co_p_dist :.3f} ({p_loss * co_p_dist :.3f} W)")
    print(f"    L   - {l_p_dist :.3f} ({p_loss * l_p_dist :.3f} W)")

    # Step 1. Derive the initial switch requirements.
    # Minimize the FOM, which is beyond the scope of this script.
    print(f"----------------------------------------")
    print(f"STEP 1")
    print(f"Deriving switch requirements.")

    (v_ds_min, i_ds_min, p_sw_min, p_sw_bud) = get_switch_requirements(
        v_out_range[2],
        i_in_range[2],
        p_transfer,
        sf=sf,
        eff_dist=sw_1_p_dist * (1 - eff),
    )

    # Our max steady state voltage applied across any one gate is v_batt when
    # there is no array hooked to the input.
    #
    # Our max steady state current is i_sc when the array is shorted to ground.
    #
    # The maximum designed power dissipation is based off of the maximum input
    # power of the array and the converter efficiency.
    print(
        f"Expected requirements for switch:"
        f"\n\tV_DS\t>= {v_ds_min :.3f} V"
        f"\n\tI_D\t>= {i_ds_min :.3f} A"
        f"\n\tP_D\t> {p_sw_min :.3f} W"
        f"\n\tP_B\t<= {p_sw_bud :.3f} W"
    )

    # Step 2. Frequency mapping at various operating points.
    # Determine the minimum required switching frequency to hit all our
    # operating points.
    if not SKIP_FOM_SEARCH:
        print(f"----------------------------------------")
        print(f"STEP 2")

        # Research switches and provide the best 25% median FOM, which we'll use to
        # find the best tradeoff.
        print(f"Find switches and report back with top 25% median FOM/tau.")
        tau = float(input("FOM/TAU (ps): ")) * 10**-12

        print(f"\nDisplaying f_sw_max for various operating points.")

        # OPERATING POINT: [V_IN, I_IN, V_OUT]
        operating_points = [
            [
                "MPP, VO_AVG",
                v_in_range[1],
                model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[1] / num_cells),
                v_out_range[1],
            ],
            [
                "VI_MIN, VO_MIN",
                v_in_range[0],
                model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[0] / num_cells),
                v_out_range[0],
            ],
            [
                "VI_MIN, VO_MAX",
                v_in_range[0],
                model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[0] / num_cells),
                v_out_range[2],
            ],
            [
                "VI_MAX, VO_MIN",
                v_in_range[2],
                model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[2] / num_cells),
                v_out_range[0],
            ],
            [
                "VI_MAX, VO_MAX",
                v_in_range[2],
                model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[2] / num_cells),
                v_out_range[2],
            ],
        ]

        get_switch_op_fs(tau, operating_points, p_sw_bud, r_l)

    # Step 3a. After selecting a switch, generate a mapping of maximum switching
    # frequency for each input/output voltage.
    print(f"----------------------------------------")
    print(f"STEP 3A")

    # Select a switch or reset parameters.
    print(f"Select a switch or modify design parameters.")
    r_ds_on = float(input("R_DS_ON (mOhm): ")) * 10**-3
    c_oss = float(input("C_OSS (pF): ")) * 10**-12
    tau = c_oss * r_ds_on
    print(f"\nFOM for this switch: {tau * 10**12 :.3f} (ps).")

    print(f"Displaying f_sw_max for all operating points.")
    f_sw = get_switch_op_fs_map(
        v_in_range,
        v_out_range,
        r_ds_on,
        c_oss,
        p_sw_bud,
        r_l,
        model_nonideal_cell,
        num_cells,
    )
    print(
        f"Maximum frequency for the converter: {f_sw :.3f} kHz "
        "(choosing lower f_sw will violate ripple constraints.)"
    )

    # Select the switching frequency.
    print(f"\nChoose the switching frequency.")
    f_sw = int(input("f_s (kHz): ")) * 10**3

    # Step 3b. After selecting a switch, determine the amount of cooling
    # required to keep the switch happy.
    if not SKIP_THERMAL_SEARCH:
        print(f"----------------------------------------")
        print(f"STEP 3B")
        print(f"Determine thermal parameters:")
        t_amb = 60
        t_max = 100
        r_jb = float(input("R_JB (C/W): "))
        r_jc = float(input("R_JC (C/W): "))
        area_hs = float(input("Area of heatsink (mm^2): ")) * 1e-6
        r_sa = float(input("R_SA (C/W): "))

        print(f"Displaying thermal area budget.\n")
        therm_area = get_switch_thermals(
            t_amb, t_max, p_sw_bud, r_jb, r_jc, r_sa, area_hs, 250
        )  # Assume at least 250 vias

        print(
            f"Minimum required thermal area per switch to dissipate heat from {t_amb} C to "
            f"{t_max} C: {therm_area * 10000 :.3f} cm^2 ({therm_area * 1000000 :.3f} mm^2)."
        )

    # Step 4. Generate a duty cycle map.
    print(f"----------------------------------------")
    print(f"STEP 4")
    print(f"Displaying duty cycle map.")

    (min_duty, max_duty) = get_switch_duty_cycle_map(v_in_range, v_out_range, eff)
    print(
        f"Minimum and maximum duty cycle to run the converter: [{min_duty :.3f}, {max_duty :.3f}]."
    )

    # Step 5. Determine passive requirements.
    print(f"----------------------------------------")
    print(f"STEP 5")
    print(f"Deriving capacitor requirements:")

    (ci_min, co_min, l_min, ci_vdc_min, co_vdc_min, l_a_min) = get_passive_sizing(
        v_in_range,
        v_out_range,
        f_sw,
        r_ci_v,
        r_co_v,
        r_l_a,
        eff,
        model_nonideal_cell,
        num_cells,
        sf,
    )

    print(
        f"\nExpected requirements for input capacitor:"
        f"\n\tC\t>= {ci_min * 1E6:.3f} uF"
        f"\n\tV\t>= {ci_vdc_min :.3f} V"
        f"\nExpected requirements for output capacitor:"
        f"\n\tC\t>= {co_min * 1E6:.3f} uF"
        f"\n\tV\t>= {co_vdc_min :.3f} V"
        f"\nExpected requirements for inductor:"
        f"\n\tL\t>= {l_min * 1E6:.3f} uH"
        f"\n\tI\t>= {l_a_min :.3f} A"
    )

    # Select the switching frequency.
    print(f"\nChoose the target inductance.")
    l = float(input("l (uH): ")) * 1e-6

    print(f"\nUsing TDK N97 material datasheet, choose a B_SAT.")
    b_sat = float(input("b_sat (mT): ")) * 1e-3

    # Step 6. Determine inductor specific requirements.
    (k_g_max, k_g_actual, b_ac, N, A_w, l_w, r, p_cond) = get_inductor_sizing(
        l, l_a_min, b_sat, r_l
    )

    print(
        f"\nK_G Comparison: {k_g_max :.3f} (Max) >= {k_g_actual :.3f} (Actual)"
        f"\nB_AC: {b_ac * 1E3 :.3f} mT"
        f"\nNumber of turns: {N}"
        f"\nWire area: {A_w * 1E6 :.3f} mm^2"
        f"\nWire length: {l_w * 1E2 :.3f} cm"
        f"\nConduction loss: {p_cond :.3f} W"
    )

    print(f"\nUsing TDK N97 material datasheet, choose a P_V given F_SW, B_AC.")
    p_v = float(input("P_V (kW/m^3): "))

    p_core = get_inductor_core_loss(p_v)
    print(f"\nCore loss: {p_core :.3f} W")
    print(
        f"\nYour allocated budget was {p_loss * l_p_dist :.3f} W (vs {p_cond + p_core :.3f} W)"
    )

    input("Press any key to end.")
