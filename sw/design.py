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

@version    0.0.0
@date       2023-02-02
"""

import argparse
import math as m
import os
import sys
from itertools import combinations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib import cm
from nonideal_model import model_nonideal_cell

fig = plt.figure()


def get_losses(v_in, i_in, v_out, f_s, r_ds_on, c_oss, r_l):
    duty = 1 - v_in / v_out
    tau = c_oss * r_ds_on

    sw1_a = (2 * i_in * r_l * f_s) / duty
    sw1_b = i_in * (1 - r_l)

    sw2_a = -(2 * i_in * r_l * f_s) / (1 - duty)
    sw2_b = i_in * (1 + (2 / (1 - duty) * r_l) - r_l)

    i_sw1_rms = m.sqrt(
        (sw1_a**2 * duty**3) / (3 * f_s**2)
        + (sw1_a * sw1_b * duty**2) / f_s
        + sw1_b**2 * duty
    )
    i_sw2_rms = m.sqrt(
        (sw2_a**2 * (1 - duty) ** 3) / (3 * f_s**2)
        + (sw2_a * sw2_b * (1 - duty) ** 2) / f_s
        + sw2_b**2 * (1 - duty)
    )

    loss_con = (i_sw1_rms**2 + i_sw2_rms**2) * r_ds_on
    loss_swi = (2 * v_out**2 * f_s * tau) / r_ds_on
    loss_tot = loss_con + loss_swi

    return loss_con, loss_swi, loss_tot


def maximize_f_sw(v_in, i_in, v_out, c_oss, r_ds_on, p_max, r_l):
    best_f_sw = 1
    while True:
        new_f_sw = best_f_sw * 1.01
        p_conduction, p_switching, p_total = get_losses(
            v_in, i_in, v_out, new_f_sw, r_ds_on, c_oss, r_l
        )
        if p_total > p_max:
            break
        else:
            best_f_sw = new_f_sw
    return best_f_sw, p_conduction, p_switching, p_total


def maximize_f_sw_tau(v_in, i_in, v_out, tau, p_max, r_l):
    f_sw_candidates = []
    r_ds_on_candidates = []
    for r_ds_on in list(np.linspace(1e-3, 5e-1, 1500)):  # 1mOhm to 500mOhm
        c_oss = tau / r_ds_on
        best_f_sw, _, _, _ = maximize_f_sw(
            v_in, i_in, v_out, c_oss, r_ds_on, p_max, r_l
        )
        if best_f_sw == 1:
            break
        else:
            r_ds_on_candidates.append(r_ds_on)
            f_sw_candidates.append(best_f_sw)

    return r_ds_on_candidates, f_sw_candidates


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    plt.ion()

    # Given a set of inputs
    num_cells = 111
    v_oc = 0.721
    i_sc = 6.15
    v_mpp = 0.621
    i_mpp = 5.84
    # Note that we get divide by 0 errors should the lower bounds be 0% or 100%
    # of the array voltage. DON'T DO IT!
    # only run input at top 75% of VIN candidates less than VMPP, and top 25% of VIN candidates greater than VMPP
    lower_end_top_percentile = 0.75
    upper_end_top_percentile = 0.25
    v_in_range = [
        (v_mpp * num_cells) * (1 - lower_end_top_percentile),
        ((v_oc - v_mpp) * upper_end_top_percentile * num_cells) + (v_mpp * num_cells),
    ]

    v_in_opt = num_cells * v_mpp  # V
    v_out_range = [80, 130]  # V
    i_in_range = [0, i_sc]  # A

    # And a specified efficiency and ripple
    eff = 0.985
    r_ci_v = 0.725  # V
    r_co_v = 1.000  # V
    r_l_a = 1.23  # A
    r_ci = r_ci_v / v_in_range[1] / 2
    r_co = r_co_v / v_out_range[1] / 2
    r_l = r_l_a / i_in_range[1] / 2

    # Power dissipation distribution
    sw_pd = 0.3
    c_pd = 0.02
    l_pd = 1 - (sw_pd * 2) - (c_pd * 2)

    p_transfer = v_in_opt * i_mpp
    p_max_diss = p_transfer * (1 - eff)
    p_sw = p_max_diss * sw_pd
    p_cap = p_max_diss * c_pd
    p_ind = p_max_diss * l_pd

    # Safety Factor. The higher the safety factor, the less likely things break.
    sf = 1.25

    # Step 0. Print out the specified design parameters.
    print(f"----------------------------------------")
    print(f"STEP 0")
    print(f"Displaying user design criteria:\n")

    print(f"Input load:")
    print(f"    {v_in_range[0] :.3f} - {v_in_range[1] :.3f} V")
    print(f"    {i_in_range[0] :.3f} - {i_in_range[1] :.3f} A")
    print(f"Output load:")
    print(f"    {v_out_range[0] :.3f} - {v_out_range[1] :.3f} V")
    print(f"Device Target Efficiency: {eff :.3f}")
    print(f"    Target Max Power Loss {p_max_diss :.3f} W")
    print(f"Power Loss Allocation:")
    print(f"    SW1, SW2 - {sw_pd :.3f} ({p_sw :.3f} W) ea.")
    print(f"    C_I, C_O - {c_pd :.3f} ({p_cap :.3f} W) ea.")
    print(f"    L - {l_pd :.3f} ({p_ind :.3f} W)")
    print(f"Maximum allowable ripple:")
    print(f"    R_CI - {r_ci_v :.3f} V [{r_ci*100 :.3f} %]")
    print(f"    R_CO - {r_co_v :.3f} V [{r_co*100 :.3f} %]")
    print(f"    R_L - {r_l_a :.3f} A [{r_l*100 :.3f} %]")
    print(f"Safety Factor: {sf :.3f}")

    # Step 1. Derive the initial switch requirements.
    # Minimize the FOM, which is beyond the scope of this script.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 1")
    print(f"Deriving switch requirements.\n")

    v_ds_min = v_out_range[1] * sf
    i_ds_min = i_in_range[1] * sf
    p_sw_min = v_in_opt * i_mpp * (1 - eff) * sf * sw_pd

    # Our max steady state voltage applied across any one gate is v_batt when
    # there is no array hooked to the input.
    print(f"Switch lower bound V_DS maximum rating: {v_ds_min :.3f} V")

    # Our max steady state current is i_sc when the array is shorted to ground.
    print(f"Switch lower bound I_DS maximum rating: {i_ds_min :.3f} A")

    # The maximum designed power dissipation is based off of the maximum input
    # power of the array and the converter efficiency.
    print(f"Switch minimum power dissipation: {p_sw_min :.3f} W")

    # Research switches and provide the best 25% median FOM, which we'll use to
    # find the best tradeoff.
    print(f"\nFind switches and report back with top 25% median FOM/tau.")
    tau = float(input("FOM/TAU (ps): ")) * 10**-12

    # Given Tau, plot r_ds_on vs max_freq for potential operating points.
    print(f"Switch power budget: {p_sw :.3f} W")

    # Step 2. Use the expected FOM to derive a plot mapping frequency at various
    # operating points.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 2")
    print(f"Displaying f_sw_max for various operating points.\n")

    # OPERATING POINT: [V_IN, I_IN, V_OUT]
    operating_points = [
        [
            "MPP, VO_AVG",
            v_in_opt,
            model_nonideal_cell(1000, 298.15, 0, 100, v_in_opt / num_cells),
            (v_out_range[0] + v_out_range[1]) / 2,
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
            v_out_range[1],
        ],
        [
            "VI_MAX, VO_MIN",
            v_in_range[1],
            model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[1] / num_cells),
            v_out_range[0],
        ],
        [
            "VI_MAX, VO_MAX",
            v_in_range[1],
            model_nonideal_cell(1000, 298.15, 0, 100, v_in_range[1] / num_cells),
            v_out_range[1],
        ],
    ]

    plt.clf()
    ax_tau_mpp = fig.add_subplot()

    worst_max_fs = 1_000_000
    worst_op = None
    for name, v_in, i_in, v_out in operating_points:
        print(
            f"{name}: {v_in :.3f} V, {i_in :.3f} A -> {v_out :.3f} V ({v_in * i_in :.3f} W)"
        )
        r_ds_on_candidates, f_sw_candidates = maximize_f_sw_tau(
            v_in, i_in, v_out, tau, p_sw, r_l
        )
        max_fs = max(f_sw_candidates)
        if worst_max_fs > max_fs:
            worst_max_fs = max_fs
            worst_op = name

        ax_tau_mpp.plot(r_ds_on_candidates, f_sw_candidates, label=name)

    ax_tau_mpp.legend()
    ax_tau_mpp.set_title(f"Max Freq vs R_DS_ON for tau={tau * 10**12 :.3f} ps")
    ax_tau_mpp.set_xlabel("R_DS_ON (Ohm)")
    ax_tau_mpp.set_ylabel("Switching Frequency (Hz)")
    ax_tau_mpp.grid()

    plt.tight_layout()
    plt.savefig("r_ds_on_and_f_sw_mapping.png")
    plt.show()

    print(
        f"With these operating points, it looks like at {worst_op} limits the "
        f"system. At the optimal R_DS_ON, it cannot run higher than "
        f"{int(worst_max_fs)} Hz without failing the allotted power budget."
    )

    print(
        "If satisfied with this, move to the next step. Otherwise, restart "
        "w/ any of the following changes: "
        "\n - different FOM"
        "\n - different I/O bounds"
        "\n - different power loss budget"
    )

    # Step 3. After selecting the switch, calculate the FOM. We then determine
    # the maximum switching frequency across the input/output map that meets our
    # efficiency metric.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 3")
    print(f"Displaying f_sw_max for all operating points.\n")

    # Select the switch and provide the switching characteristics.
    print(f"Choose switch and report back with C_OSS, R_DS_ON.")
    c_oss = float(input("C_OSS (pF): ")) * 10**-12
    r_ds_on = float(input("R_DS_ON (mOhm): ")) * 10**-3

    tau = c_oss * r_ds_on
    print(f"FOM for this switch: {tau * 10**12 :.3f} (ps).")
    print(f"Generating f_s_max surface map.")

    x_v_in = []
    y_v_out = []
    z_f_s = []

    v_in_combos = np.linspace(v_in_range[0], v_in_range[1], num=30, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[1], num=30, endpoint=True)
    for v_in in v_in_combos:
        i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
        for v_out in v_out_combos:
            f_sw, _, _, _ = maximize_f_sw(v_in, i_in, v_out, c_oss, r_ds_on, p_sw, r_l)
            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_f_s.append(f_sw * 10**-3)

    plt.clf()

    # Plot out switching frequency map.
    ax_freq = fig.add_subplot(projection="3d")
    ax_freq.scatter(x_v_in, y_v_out, z_f_s, c=z_f_s)
    ax_freq.set_title("Max Frequency within Power Budget Across I/O Mapping")
    ax_freq.set_xlabel("V_IN (V)")
    ax_freq.set_ylabel("V_OUT (V)")
    ax_freq.set_zlabel("F_S_MAX (kHz)")

    plt.savefig("frequency_operation_map.png")
    plt.show()

    # Determine minimum frequency allowed across the map.
    print(
        f"Maximum frequency for the converter: {m.floor(min(z_f_s)) :.3f} kHz "
        "(choosing lower is acceptable but will result in larger ripple.)"
    )

    # Select the switching frequency.
    print(f"Choose the switching frequency.")
    f_sw = int(input("f_s (kHz): ")) * 10**3



    # Step 4. Plot duty cycle ratio for input/output combos.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 4")
    print(f"Generating duty cycle surface map.\n")

    x_v_in = []
    y_v_out = []
    z_duty = []
    for v_in in np.linspace(v_in_range[0], v_in_range[1], num=50, endpoint=True):
        for v_out in np.linspace(v_out_range[0], v_out_range[1], num=50, endpoint=True):
            duty = 1 - v_in / v_out
            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_duty.append(duty)

    # Plot out switching frequency map.
    plt.clf()
    ax_duty = fig.add_subplot(projection="3d")
    ax_duty.scatter(x_v_in, y_v_out, z_duty, c=z_duty)
    ax_duty.set_title("Minimum Duty Cycle Across I/O Mapping")
    ax_duty.set_xlabel("V_IN (V)")
    ax_duty.set_ylabel("V_OUT (V)")
    ax_duty.set_zlabel("Duty Cycle")

    min_duty = np.min(z_duty)
    max_duty = np.max(z_duty)

    print(f"Min duty cycle {min_duty * 100 :.3f} %")
    print(f"Max duty cycle {max_duty * 100 :.3f} %")

    # print(
    #     "Note that if the next step fails, R_DS_ON is probably too high. "
    #     "The following actions can be performed:"
    #     "\n    - tradeoff r_ds_on for higher c_oss (you'll probably find yourself here)"
    #     "\n    - increase min v_in relative to v_out to reduce max duty (a reasonable option)"
    #     "\n    - decrease max v_out relative to v_in to reduce max duty (a less reasonable option)"
    #     "\n    - decrease design efficiency (undesirable for MPPT, last resort)"
    # )

    plt.tight_layout()
    plt.savefig("duty_surface_map.png")
    plt.show()



    # Step 5. Derive capacitor requirements.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 5")
    print(f"Deriving capacitor requirements:\n")

    # Given that the PV is a nonlinear current source, it's not directly
    # straightforward to determine when ci, co, l are minimized. We do know,
    # however, that the minimum feasible passive value is bounded by the worst
    # input/output combo.
    ci_min = []
    co_min = []
    l_min = []

    v_in_combos = np.linspace(v_in_range[0], v_in_range[1], num=50, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[1], num=50, endpoint=True)
    for v_in in v_in_combos:
        i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
        p_in = v_in * i_in
        for v_out in v_out_combos:
            ci_min.append((r_l * i_in) / (8 * r_ci * v_out * f_sw))
            co_min.append((v_out - v_in) * p_in / (2 * r_co * v_out**3 * f_sw))
            l_min.append((v_in - v_in**2 / v_out) / (2 * i_in * f_sw * r_l))

    ci_min = np.max(ci_min)
    co_min = np.max(co_min)
    l_min = np.max(l_min)
    ci_vdc_min = (v_in_range[1] + r_ci_v) * sf
    co_vdc_min = (v_out_range[1] + r_co_v) * sf

    print(f"Minimum C_IN: {ci_min * 10**6 :.3f} uF")
    print(f"Minimum C_OUT: {co_min * 10**6 :.3f} uF")
    print(f"Minimum L: {l_min * 10**6 :.3f} uH")
    print(f"Input capacitor should be rated for: {ci_vdc_min :.3f} V.")
    print(f"Output capacitor should be rated for: {co_vdc_min :.3f} V.")



    # Step 6. Derive inductor requirements.
    input("Press any key to continue.\n")
    print(f"----------------------------------------")
    print(f"STEP 6")
    print(f"Deriving inductor requirements:\n")

    print(f"Inductor should be rated for {(i_mpp + r_l_a) * sf :.3f} A.")
    print(f"KG method.")
    print(f"")


    input("Press any key to end.")
