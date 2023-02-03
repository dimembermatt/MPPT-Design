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
import math
import os
import sys
from itertools import combinations
from math import sqrt

import matplotlib.pyplot as plt
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

    i_sw1_rms = sqrt(
        (sw1_a**2 * duty**3) / (3 * f_s**2)
        + (sw1_a * sw1_b * duty**2) / f_s
        + sw1_b**2 * duty
    )
    i_sw2_rms = sqrt(
        (sw2_a**2 * (1 - duty) ** 3) / (3 * f_s**2)
        + (sw2_a * sw2_b * (1 - duty) ** 2) / f_s
        + sw2_b**2 * (1 - duty)
    )

    loss_con = (i_sw1_rms**2 + i_sw2_rms**2) * r_ds_on
    loss_swi = (2 * v_out**2 * f_s * tau) / r_ds_on
    loss_tot = loss_con + loss_swi

    return loss_con, loss_swi, loss_tot


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
    v_in_range = [num_cells * v_oc * 0.05, num_cells * v_oc * 0.95]  # V
    v_in_opt = num_cells * v_mpp  # V
    v_out_range = [80, 134.4]  # V
    i_in_range = [0, i_sc]  # A

    # And a specified efficiency and ripple
    eff = 0.975
    r_ci_v = 0.1  # V
    r_co_v = 0.1  # V
    r_l_a = 0.05  # A
    r_ci = r_ci_v / v_in_range[1]
    r_co = r_co_v / v_out_range[1]
    r_l = r_l_a / i_in_range[1]

    # Safety Factor. The higher the safety factor, the less likely things break.
    sf = 1.5

    # Step 0. Print out the specified design parameters.
    print(f"----------------------------------------")
    print(f"STEP 0")
    print(f"User design criteria: ")
    print(f"Input load:")
    print(f"    {v_in_range[0]}-{v_in_range[1]} V")
    print(f"    {i_in_range[0]}-{i_in_range[1]} A")
    print(f"Output load:")
    print(f"    {v_out_range[0]}-{v_out_range[1]} V")
    print(f"Device Efficiency: {eff}")
    print(f"Maximum allowable ripple:")
    print(f"    R_CI - {r_ci_v} V [{r_ci*100} %]")
    print(f"    R_CO - {r_co_v} V [{r_co*100} %]")
    print(f"    R_L - {r_l_a} A [{r_l*100} %]")
    print(f"Safety Factor: {sf}")

    # Step A. Plot duty cycle ratio for input/output combos.
    print(f"----------------------------------------")
    print(f"STEP A")
    print(
        f"Generating duty cycle surface map."
    )

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
    ax_duty = fig.add_subplot(projection="3d")
    ax_duty.scatter(x_v_in, y_v_out, z_duty, c=z_duty)
    ax_duty.set_title("Minimum Duty Cycle Across I/O Mapping")
    ax_duty.set_xlabel("V_IN (V)")
    ax_duty.set_ylabel("V_OUT (V)")
    ax_duty.set_zlabel("Duty Cycle")

    print(
        "Note that if the next step fails, R_DS_ON is probably too high. "
        "The following actions can be performed:"
        "\n\t- tradeoff r_ds_on for higher c_oss (you'll probably find yourself here)"
        "\n\t- increase min v_in relative to v_out to reduce max duty (a reasonable option)"
        "\n\t- decrease max v_out relative to v_in to reduce max duty (a less reasonable option)"
        "\n\t- decrease design efficiency (undesirable for MPPT, last resort)"
    )

    plt.show()


    # Step 1. Derive the initial switch requirements and choose a switch.
    # Minimize the FOM, which is beyond the scope of this script.
    print(f"----------------------------------------")
    print(f"STEP 1")

    # Our max steady state voltage applied across any one gate is v_batt when
    # there is no array hooked to the input.
    print(f"\nSwitch lower bound V_DS maximum rating: {v_out_range[1] * sf} V")

    # Our max steady state current is i_sc when the array is shorted to ground.
    print(f"Switch lower bound I_DS maximum rating: {i_mpp * sf} A")

    # The maximum designed power dissipation is based off of the maximum input
    # power of the array and the converter efficiency.
    print(f"Switch minimum power dissipation: {v_in_opt * i_mpp * (1 - eff) * sf} W")

    # Select the switch and provide the switching characteristics.
    print(f"\nChoose switch and report back with worst case C_OSS, R_DS_ON.")
    c_oss = float(input("C_OSS (pF): ")) * 10**-12
    r_ds_on = float(input("R_DS_ON (mOhm): ")) * 10**-3


    # Step 2. After selecting the switch, calculate the FOM. We then determine
    # the maximum switching frequency across the input/output map that meets our
    # efficiency metric.
    print(f"----------------------------------------")
    print(f"STEP 2")
    tau = c_oss * r_ds_on
    print(f"FOM for this switch: {tau * 10**12} (ps).")
    print(
        f"Generating f_s_max surface map complying w/ device efficiency "
        f"({v_in_opt * i_mpp * (1 - eff)} W max dissipation)."
    )

    x_v_in = []
    y_v_out = []
    z_f_s = []

    v_in_combos = np.linspace(v_in_range[0], v_in_range[1], num=50, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[1], num=50, endpoint=True)
    for v_in in v_in_combos:
        i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
        for v_out in v_out_combos:
            f_s = 1e3

            # Find the maximum frequency that is within spec.
            while True:
                loss_con, loss_swi, loss_tot = get_losses(
                    v_in, i_in, v_out, f_s, r_ds_on, c_oss, r_l
                )
                if loss_tot >= v_in_opt * i_mpp * (1 - eff):
                    break
                f_s *= 1.025

            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_f_s.append(f_s * 10**-3)

    plt.clf()

    # Plot out switching frequency map.
    ax_freq = fig.add_subplot(projection="3d")
    ax_freq.scatter(x_v_in, y_v_out, z_f_s, c=z_f_s)
    ax_freq.set_title("Max Frequency within Power Budget Across I/O Mapping")
    ax_freq.set_xlabel("V_IN (V)")
    ax_freq.set_ylabel("V_OUT (V)")
    ax_freq.set_zlabel("F_S_MAX (kHz)")

    plt.show()

    # Determine minimum frequency allowed across the map.
    print(
        f"Minimum frequency for the converter: {math.floor(min(z_f_s))} kHz "
        "(choosing lower is acceptable but will result in larger ripple.)"
    )

    # Select the switching frequency.
    print(f"\nChoose the switching frequency.")
    f_s = int(input("f_s (kHz): ")) * 10**3

    # Step 3. Given the minimum switching frequency, derive the passives.
    print(f"----------------------------------------")
    print(f"STEP 3")

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
            ci_min.append((r_l * i_in) / (8 * r_ci * v_out * f_s))
            co_min.append((v_out - v_in) * p_in / (2 * r_co * v_out**3 * f_s))
            l_min.append((v_in - v_in**2 / v_out) / (2 * i_in * f_s * r_l))

    print(f"Minimum C_IN: {np.max(ci_min) * 10**6} uF")
    print(f"Minimum C_OUT: {np.max(co_min) * 10**6} uF")
    print(f"Minimum L: {np.max(l_min) * 10**6} uH")
    print(
        f"Capacitors and inductors should be rated for {v_out_range[1] * sf} V and {i_mpp * sf} A."
    )

    input("Press any key to end.")
