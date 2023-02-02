"""_summary_
@file       design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate parameters of a DC-DC boost converter.
@version    0.0.0
@date       2023-02-02
"""

import argparse
import os
import sys
from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from nonideal_model import model_nonideal_cell

fig = plt.figure()

if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    # Given a set of inputs
    num_cells = 111
    v_in_range = [1, num_cells * 0.721]  # V
    v_out_range = [80, 134.4]  # V
    i_in_range = [0, 6.15]  # A

    # And a specified efficiency and ripple
    eff = 0.99
    r_ci_v = 1  # V
    r_co_v = 1  # V
    r_l_a = 0.05  # A
    r_ci = r_ci_v / v_in_range[1]
    r_co = r_co_v / v_out_range[1]
    r_l = r_l_a / i_in_range[1]

    # Safety Factor
    sf = 1.25

    # Step 0. Print out the specified design parameters.
    print(f"Device Efficiency: {eff}")
    print(f"Maximum allowable ripple:")
    print(f"    R_CI - {r_ci_v} V [{r_ci*100} %]")
    print(f"    R_CO - {r_co_v} V [{r_co*100} %]")
    print(f"    R_L - {r_l_a} A [{r_l*100} %]")

    # Step 1. Generate a set of v_in/v_out pairs
    # Generate surface map representing power transfer, power loss, duty cycle
    v_in_resolution = 1
    v_out_resolution = 1
    x_v_in = []
    y_v_out = []
    z_i_in = []
    z_p_in = []
    z_p_loss = []
    z_duty = []
    for v_in in np.arange(v_in_range[0], v_in_range[1], v_in_resolution):
        for v_out in np.arange(v_out_range[0], v_out_range[1], v_out_resolution):
            i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
            p_in = v_in * i_in
            p_loss = p_in * (1 - eff)
            duty = 1 - v_in / v_out

            # print(f"Input power: {p_in} W")
            # print(f"Target maximum power loss: {p_loss} W")
            # print(f"Required duty cycle: {duty}")

            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_i_in.append(i_in)
            z_p_in.append(p_in)
            z_p_loss.append(p_loss)
            z_duty.append(duty)

    ax0 = fig.add_subplot(3, 4, 1, projection="3d")
    ax0.scatter(x_v_in, y_v_out, z_i_in, c=z_i_in)
    ax0.set_title("I_IN")
    ax0.set_xlabel("V_IN (V)")
    ax0.set_ylabel("V_OUT (V)")
    ax0.set_zlabel("I_IN (A)")

    ax1 = fig.add_subplot(3, 4, 2, projection="3d")
    ax1.scatter(x_v_in, y_v_out, z_p_in, c=z_p_in)
    ax1.set_title("P_IN")
    ax1.set_xlabel("V_IN (V)")
    ax1.set_ylabel("V_OUT (V)")
    ax1.set_zlabel("P_IN (W)")

    ax2 = fig.add_subplot(3, 4, 4, projection="3d")
    ax2.scatter(x_v_in, y_v_out, z_p_loss, c=z_p_loss)
    ax2.set_title("P_LOSS")
    ax2.set_xlabel("V_IN (V)")
    ax2.set_ylabel("V_OUT (V)")
    ax2.set_zlabel("P_LOSS (W)")

    ax3 = fig.add_subplot(3, 4, 3, projection="3d")
    ax3.scatter(x_v_in, y_v_out, z_duty, c=z_duty)
    ax3.set_title("DUTY")
    ax3.set_xlabel("V_IN (V)")
    ax3.set_ylabel("V_OUT (V)")
    ax3.set_zlabel("DUTY")

    # Step 2. For the set if input and output voltages, derive the switch
    # requirements for the worst case scenario.
    v_sw_ds_min = sf * np.max(v_out)
    print(f"Switch lower bound V_ds maximum rating: {v_sw_ds_min} V")

    avg_i_l = np.divide(z_p_in, x_v_in)
    avg_i_sw_2 = np.divide(z_p_in, y_v_out)
    avg_i_sw_1 = np.subtract(avg_i_l, avg_i_sw_2)
    i_sw_ds_min = sf * np.max([np.max(avg_i_sw_1), np.max(avg_i_sw_2)])
    print(f"Switch lower bound I_ds maximum rating: {i_sw_ds_min} A")

    # Step 3. After selecting the switch, calculate the FOM
    c_oss = input("C_OSS (F)")
    r_ds_on = input("R_DS_ON (Ohm)")
    tau = c_oss * r_ds_on
    print(f"FOM for this switch: {tau} (s)")

    # Step 4. Determine the maximum switching frequency given the switch FOM.
    # Step 5. Determine the minimum dead time to drive at ZVS.
    # Step 6. Determine minimum inductance and capacitances required to drive at
    # the desired switching frequency.
    z_f_max = []
    z_f_max_soft = []
    z_dead = []
    z_l_min = []
    z_ci_min = []
    z_co_min = []
    for v_in in np.arange(v_in_range[0], v_in_range[1], v_in_resolution):
        for v_out in np.arange(v_out_range[0], v_out_range[1], v_out_resolution):
            i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
            p_in = v_in * i_in
            p_loss = p_in * (1 - eff)

            f_max = ((p_loss / p_in) ** 2 * (v_out / v_in) ** 2) / (
                8 * (1 / 3 * r_l**2 + 1) * tau
            )
            z_f_max.append(f_max)

            f_max_soft = ((p_loss / p_in) ** 2 * (v_out / v_in) ** 2) / (
                4 * (1 / 3 * r_l**2 + 1) * tau
            )

            z_f_max_soft.append(f_max_soft)

            dead_time = (2 * c_oss * v_in * v_out / (p_in * (1 - r_l))) * 10**-9
            z_dead.append(dead_time)

            l_min = (v_out - v_in) * v_in / (2 * r_l * p_in * v_out * f_max) * 10**-6
            z_l_min.append(l_min)

            ci_min = (r_l * p_in) / (8 * r_ci * v_in**2 * f_max) * 10**-6
            z_ci_min.append(ci_min)

            co_min = (
                ((v_out - v_in) * p_in) / (2 * r_co * v_out**3 * f_max) * 10**-6
            )
            z_co_min.append(co_min)

    ax5 = fig.add_subplot(3, 4, 5, projection="3d")
    ax5.scatter(x_v_in, y_v_out, z_f_max, c=z_f_max)
    ax5.set_title("Max Switching Frequency")
    ax5.set_xlabel("V_IN (V)")
    ax5.set_ylabel("V_OUT (V)")
    ax5.set_zlabel("Switching Frequency (Hz)")

    ax6 = fig.add_subplot(3, 4, 6, projection="3d")
    ax6.scatter(x_v_in, y_v_out, z_f_max_soft, c=z_f_max_soft)
    ax6.set_title("Max Soft Switching Frequency")
    ax6.set_xlabel("V_IN (V)")
    ax6.set_ylabel("V_OUT (V)")
    ax6.set_zlabel("Soft Switching Frequency (Hz)")

    ax7 = fig.add_subplot(3, 4, 7, projection="3d")
    ax7.scatter(x_v_in, y_v_out, z_dead, c=z_dead)
    ax7.set_title("Min Dead Time for Soft Switching")
    ax7.set_xlabel("V_IN (V)")
    ax7.set_ylabel("V_OUT (V)")
    ax7.set_zlabel("Min Dead Time (ns)")

    ax8 = fig.add_subplot(3, 4, 8, projection="3d")
    ax8.scatter(x_v_in, y_v_out, z_l_min, c=z_l_min)
    ax8.set_title("Minimum Inductance")
    ax8.set_xlabel("V_IN (V)")
    ax8.set_ylabel("V_OUT (V)")
    ax8.set_zlabel("Min Inductance (uH)")

    ax9 = fig.add_subplot(3, 4, 9, projection="3d")
    ax9.scatter(x_v_in, y_v_out, z_ci_min, c=z_ci_min)
    ax9.set_title("Minimum Input Capacitance")
    ax9.set_xlabel("V_IN (V)")
    ax9.set_ylabel("V_OUT (V)")
    ax9.set_zlabel("Min Inp. Capacitance (uF)")

    ax10 = fig.add_subplot(3, 4, 10, projection="3d")
    ax10.scatter(x_v_in, y_v_out, z_co_min, c=z_co_min)
    ax10.set_title("Minimum Output Capacitance")
    ax10.set_xlabel("V_IN (V)")
    ax10.set_ylabel("V_OUT (V)")
    ax10.set_zlabel("Min Out. Capacitance (uF)")

    print(f"Minimum suggested c_in: {np.min(z_ci_min) * 10 ** -6} (uF)")
    print(f"Minimum suggested c_out: {np.min(z_co_min) * 10 ** -6} (uF)")
    print(f"Minimum suggested l: {np.min(z_l_min) * 10 ** -6} (uH)")

    c_in = input("C_IN (F)")
    c_out = input("C_OUT (F)")
    l = input("L (H)")

    # Step 7. Determine the switching and conductance losses caused by the
    # circuit.
    z_conduction = []
    z_switching = []
    z_soft_switching = []
    z_total = []
    z_soft_total = []
    for v_in in np.arange(v_in_range[0], v_in_range[1], v_in_resolution):
        for v_out in np.arange(v_out_range[0], v_out_range[1], v_out_resolution):
            i_in = model_nonideal_cell(1000, 298.15, 0, 100, v_in / num_cells)
            p_in = v_in * i_in
            p_loss = p_in * (1 - eff)
            duty = 1 - v_in / v_out

            f_max = ((p_loss / p_in) ** 2 * (v_out / v_in) ** 2) / (
                8 * (1 / 3 * r_l**2 + 1) * tau
            )

            f_max_soft = ((p_loss / p_in) ** 2 * (v_out / v_in) ** 2) / (
                4 * (1 / 3 * r_l**2 + 1) * tau
            )

            sw1_a = (2 * i_in * r_l * f_max) / duty
            sw1_b = i_in * (1 - r_l)

            sw2_a = -(2 * i_in * r_l * f_max) / (1 - duty)
            sw2_b = i_in * (1 + (2 / (1 - duty) * r_l) - r_l)

            i_sw1_rms = sqrt(
                (sw1_a**2 * duty**3) / (3 * f_max**2)
                + (sw1_a * sw1_b * duty**2) / f_max
                + sw1_b**2 * duty
            )
            i_sw2_rms = sqrt(
                (sw2_a**2 * (1 - duty) ** 3) / (3 * f_max**2)
                + (sw2_a * sw2_b * (1 - duty) ** 2) / f_max
                + sw2_b**2 * (1 - duty)
            )

            conduction_loss = (i_sw1_rms**2 + i_sw2_rms**2) * r_ds_on
            switching_loss = (2 * v_out**2 * f_max * tau) / r_ds_on
            switching_loss_soft = switching_loss / 2

            z_conduction.append(conduction_loss)
            z_switching.append(switching_loss)
            z_soft_switching.append(switching_loss_soft)
            z_total.append(conduction_loss + switching_loss)
            z_soft_total.append(conduction_loss + switching_loss_soft)

    ax11 = fig.add_subplot(3, 4, 11, projection="3d")
    ax11.scatter(x_v_in, y_v_out, z_conduction, c=z_conduction)
    ax11.scatter(x_v_in, y_v_out, z_switching, c=z_switching)
    ax11.scatter(x_v_in, y_v_out, z_total, c=z_total)
    ax11.set_title("Switch Losses")
    ax11.set_xlabel("V_IN (V)")
    ax11.set_ylabel("V_OUT (V)")
    ax11.set_zlabel("Switch Losses (W)")

    ax12 = fig.add_subplot(3, 4, 12, projection="3d")
    ax12.scatter(x_v_in, y_v_out, z_conduction, c=z_conduction)
    ax12.scatter(x_v_in, y_v_out, z_soft_switching, c=z_soft_switching)
    ax12.scatter(x_v_in, y_v_out, z_soft_total, c=z_soft_total)
    ax12.set_title("Switch Losses (Soft)")
    ax12.set_xlabel("V_IN (V)")
    ax12.set_ylabel("V_OUT (V)")
    ax12.set_zlabel("Switch Losses (W)")

    plt.tight_layout()
    plt.show()
