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
    v_in_range = [num_cells * v_oc * 0.25, num_cells * v_oc * 0.95]  # V
    v_in_opt = num_cells * v_mpp  # V
    v_out_range = [80, 134.4 * 0.96]  # V
    i_in_range = [0, i_sc]  # A

    # And a specified efficiency and ripple
    eff = 0.99
    r_ci_v = 1  # V
    r_co_v = 0.1  # V
    r_l_a = 1.5  # A
    r_ci = r_ci_v / v_in_range[1] / 2
    r_co = r_co_v / v_out_range[1] / 2
    r_l = r_l_a / i_in_range[1] / 2

    # Safety Factor. The higher the safety factor, the less likely things break.
    sf = 1.5

    # Step 0. Print out the specified design parameters.
    print(f"----------------------------------------")
    print(f"STEP 0")
    print(f"User design criteria: ")
    print(f"Input load:")
    print(f"    {v_in_range[0] :.3f} - {v_in_range[1] :.3f} V")
    print(f"    {i_in_range[0] :.3f} - {i_in_range[1] :.3f} A")
    print(f"Output load:")
    print(f"    {v_out_range[0] :.3f} - {v_out_range[1] :.3f} V")
    print(f"Device Efficiency: {eff :.3f}")
    print(f"Maximum allowable ripple:")
    print(f"    R_CI - {r_ci_v :.3f} V [{r_ci*100 :.3f} %]")
    print(f"    R_CO - {r_co_v :.3f} V [{r_co*100 :.3f} %]")
    print(f"    R_L - {r_l_a :.3f} A [{r_l*100 :.3f} %]")
    print(f"Safety Factor: {sf :.3f}")

    # Step A. Plot duty cycle ratio for input/output combos.
    print(f"----------------------------------------")
    print(f"STEP A")
    print(f"Generating duty cycle surface map.")

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
        "\n    - tradeoff r_ds_on for higher c_oss (you'll probably find yourself here)"
        "\n    - increase min v_in relative to v_out to reduce max duty (a reasonable option)"
        "\n    - decrease max v_out relative to v_in to reduce max duty (a less reasonable option)"
        "\n    - decrease design efficiency (undesirable for MPPT, last resort)"
    )

    plt.savefig("duty_surface_map.png")
    plt.show()

    # Step 1. Derive the initial switch requirements and choose a switch.
    # Minimize the FOM, which is beyond the scope of this script.
    print(f"----------------------------------------")
    print(f"STEP 1")

    # Our max steady state voltage applied across any one gate is v_batt when
    # there is no array hooked to the input.
    print(f"\nSwitch lower bound V_DS maximum rating: {v_out_range[1] * sf :.3f} V")

    # Our max steady state current is i_sc when the array is shorted to ground.
    print(f"Switch lower bound I_DS maximum rating: {i_mpp * sf :.3f} A")

    # The maximum designed power dissipation is based off of the maximum input
    # power of the array and the converter efficiency.
    print(
        f"Switch minimum power dissipation: {v_in_opt * i_mpp * (1 - eff) * sf :.3f} W"
    )

    # Research switches and provide the best 80% median FOM, which we'll use to
    # find the best tradeoff.
    print(f"\nFind switches and report back with top 80% median FOM/tau.")
    tau = float(input("FOM/TAU (ps): ")) * 10**-12

    # x: plot frequency vs y: r_ds_on vs z: power loss
    x_f_s = []
    y_r_ds_on = []
    z_cond = []
    z_switch = []
    z_tot = []
    z_max = []

    print("Frequencies plotted: 100, 1k, 10k, 100k, 1M Hz")
    for f_s in [100, 1_000, 10_000, 100_000, 1_000_000]:
        r_ds_on = 1e-4  # 100 uOhm
        for i in range(200):
            c_oss = tau / r_ds_on
            v_in = v_in_opt / num_cells
            i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in)
            p_conduction, p_switching, p_total = get_losses(
                v_in, i_in, 107.2, f_s, r_ds_on, c_oss, r_l
            )

            x_f_s.append(f_s)
            y_r_ds_on.append(r_ds_on)
            z_cond.append(p_conduction)
            z_switch.append(p_switching)
            z_tot.append(p_total)
            z_max.append(v_in_opt * i_mpp * (1 - eff) * sf)

            r_ds_on *= 1.04

    plt.clf()

    def log_tick_formatter(val, pos=None):
        return r"$10^{:.0f}$".format(val)

    # Plot out switching frequency map.
    ax_tau = fig.add_subplot(projection="3d")
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_cond),
        s=2,
        label="Conduction Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_switch),
        s=2,
        label="Switching Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_tot),
        s=2,
        label="Total Loss (W)",
    )
    ax_tau.scatter(
        np.log10(x_f_s),
        np.log10(y_r_ds_on),
        np.log10(z_max),
        s=2,
        label="Max Design Loss (W)",
    )
    ax_tau.legend()
    ax_tau.xaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.yaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.zaxis.set_major_formatter(mticker.FuncFormatter(log_tick_formatter))
    ax_tau.set_title("")
    ax_tau.set_xlabel("Switching Frequency (Hz)")
    ax_tau.set_ylabel("R_DS_ON (Ohm)")
    ax_tau.set_zlabel("Power Loss (W)")

    plt.savefig("frequency_tau_power_map.png")
    plt.show()

    print(f"\nSelect a switching frequency to investigate.")
    f_s = int(input("F_S (hz): "))

    y_r_ds_on = []
    z_cond = []
    z_switch = []
    z_tot = []
    z_max = []

    r_ds_on = 1e-4  # 100 uOhm
    for i in range(500):
        c_oss = tau / r_ds_on
        v_in = v_in_opt / num_cells
        i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in)
        p_conduction, p_switching, p_total = get_losses(
            v_in, i_in, 107.2, f_s, r_ds_on, c_oss, r_l
        )

        y_r_ds_on.append(r_ds_on)
        z_cond.append(p_conduction)
        z_switch.append(p_switching)
        z_tot.append(p_total)
        z_max.append(v_in_opt * i_mpp * (1 - eff) * sf)

        r_ds_on *= 1.02

    plt.clf()

    # Plot out switching frequency map.
    ax_tau = fig.add_subplot()
    ax_tau.scatter(y_r_ds_on, z_cond, s=2, label="Conduction Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_switch, s=2, label="Switching Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_tot, s=2, label="Total Loss (W)")
    ax_tau.scatter(y_r_ds_on, z_max, s=2, label="Max Design Loss (W)")
    ax_tau.legend()
    ax_tau.set_xscale("log")
    ax_tau.set_yscale("log")
    ax_tau.set_title("")
    ax_tau.set_xlabel("R_DS_ON (Ohm)")
    ax_tau.set_ylabel("Power Loss (W)")

    plt.savefig("tau_power_map.png")
    plt.show()

    # Select the switch and provide the switching characteristics.
    print(f"\nChoose switch and report back with C_OSS, R_DS_ON.")
    c_oss = float(input("C_OSS (pF): ")) * 10**-12
    r_ds_on = float(input("R_DS_ON (mOhm): ")) * 10**-3

    # Step 2. After selecting the switch, calculate the FOM. We then determine
    # the maximum switching frequency across the input/output map that meets our
    # efficiency metric.
    print(f"----------------------------------------")
    print(f"STEP 2")
    tau = c_oss * r_ds_on
    print(f"FOM for this switch: {tau * 10**12 :.3f} (ps).")
    print(
        f"Generating f_s_max surface map complying w/ device efficiency "
        f"({v_in_opt * i_mpp * (1 - eff) :.3f} W max dissipation)."
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

    plt.savefig("frequency_operation_map.png")
    plt.show()

    # Determine minimum frequency allowed across the map.
    print(
        f"Maximum frequency for the converter: {math.floor(min(z_f_s)) :.3f} kHz "
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

    print(f"Minimum C_IN: {np.max(ci_min) * 10**6 :.3f} uF")
    print(f"Minimum C_OUT: {np.max(co_min) * 10**6 :.3f} uF")
    print(f"Minimum L: {np.max(l_min) * 10**6 :.3f} uH")
    print(
        f"Capacitors and inductors should be rated for {v_out_range[1] * sf :.3f} V and {i_mpp * sf :.3f} A."
    )

    input("Press any key to end.")
