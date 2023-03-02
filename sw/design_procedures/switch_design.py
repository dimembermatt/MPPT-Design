"""_summary_
@file       switch_design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate design parameters of switches for a DC-DC boost converter.
@version    0.0.0
@date       2023-03-02
"""

import math as m

import matplotlib.pyplot as plt
import numpy as np


def get_switch_requirements(max_v_out, max_i_in, max_p, sf=0.25, eff_dist=0.01):
    """_summary_
    Gets switch requirements.

    Args:
        max_v_out (float): Maximum output voltage.
        max_i_in (float): Maximum input current.
        max_p (float): Maximum input power.
        sf (float, optional): Safety factor. Defaults to 0.25.
        eff_dist (float, optional): Efficiency distribution for the switches
            (per switch). Defaults to 0.01.

    Returns:
        (float, ...): Set of floats consisting of:
            Switch lower bound V_DS rating
            Switch lower bound I_DS rating
            Switch minimum power dissipation rating
            Max power budget
    """
    v_ds_min = max_v_out * sf
    i_ds_min = max_i_in * sf
    p_sw_min = max_p * eff_dist * sf
    p_sw_bud = max_p * eff_dist

    return (v_ds_min, i_ds_min, p_sw_min, p_sw_bud)


def get_switch_losses(v_in, i_in, v_out, f_sw, r_ds_on, c_oss, r_l):
    """_summary_
    Get switch losses (conduction, switching, total).

    Args:
        v_in (float): Input voltage
        i_in (float): Input current
        v_out (float): Output voltage
        f_sw (float): Switching frequency
        r_ds_on (float): Switch on resistance between drain and source
        c_oss (float): Switch output capacitance
        r_l (float): Inductor current ripple

    Returns:
        (float, ...): Set of floats consisting of:
            Conduction loss
            Switching loss
            Total loss
    """
    duty = 1 - v_in / v_out
    tau = c_oss * r_ds_on

    sw1_a = (2 * i_in * r_l * f_sw) / duty
    sw1_b = i_in * (1 - r_l)

    sw2_a = -(2 * i_in * r_l * f_sw) / (1 - duty)
    sw2_b = i_in * (1 + (2 / (1 - duty) * r_l) - r_l)

    i_sw1_rms = m.sqrt(
        (sw1_a**2 * duty**3) / (3 * f_sw**2)
        + (sw1_a * sw1_b * duty**2) / f_sw
        + sw1_b**2 * duty
    )
    i_sw2_rms = m.sqrt(
        (sw2_a**2 * (1 - duty) ** 3) / (3 * f_sw**2)
        + (sw2_a * sw2_b * (1 - duty) ** 2) / f_sw
        + sw2_b**2 * (1 - duty)
    )

    loss_con = (i_sw1_rms**2 + i_sw2_rms**2) * r_ds_on
    loss_swi = (2 * v_out**2 * f_sw * tau) / r_ds_on
    loss_tot = loss_con + loss_swi

    return (loss_con, loss_swi, loss_tot)


def maximize_f_sw(v_in, i_in, v_out, r_ds_on, c_oss, p_sw_bud, r_l):
    """_summary_
    Maximize possible switching frequency for a set of parameters.

    Args:
        v_in (float): Input voltage
        i_in (float): Input current
        v_out (float): Output voltage
        r_ds_on (float): Switch on resistance between drain and source
        c_oss (float): Switch output capacitance
        p_sw_bud (float): Maximum budget for switch loss
        r_l (float): Inductor current ripple

    Returns:
        (float, ...): Set of floats consisting of:
            Best possible switching frequency for this set of parameters
            Conduction loss
            Switching loss
            Total loss
    """

    best_f_sw = 1
    while True:
        new_f_sw = best_f_sw * 1.01
        p_conduction, p_switching, p_total = get_switch_losses(
            v_in, i_in, v_out, new_f_sw, r_ds_on, c_oss, r_l
        )
        if p_total > p_sw_bud:
            break
        else:
            best_f_sw = new_f_sw
    return (best_f_sw, p_conduction, p_switching, p_total)


def get_switch_op_fs(tau, operating_points, p_sw_bud, r_l):
    """_summary_
    Generate a map across key operating points determining optimal R_DS_ON to
    maximize F_SW for a given power budget and inductor ripple.

    Args:
        tau (float): FOM. ps
        operating_points ([[str, float, float, float], ...]): set of operating
            points in format [name, v_in, i_in, v_out] to test
        p_sw_bud (float): Power budget alloted for switch
        r_l (float): Inductor current ripple ratio

    Returns:
        (str, float): Name of the worst performing operating point and the max
            F_SW for that operating point.
    """

    def maximize_f_sw_tau(v_in, i_in, v_out, tau, p_sw_bud, r_l):
        f_sw_candidates = []
        r_ds_on_candidates = []
        for r_ds_on in list(np.linspace(1e-3, 5e-1, 1500)):  # 1mOhm to 500mOhm
            c_oss = tau / r_ds_on
            best_f_sw, _, _, _ = maximize_f_sw(
                v_in, i_in, v_out, r_ds_on, c_oss, p_sw_bud, r_l
            )
            if best_f_sw == 1:
                break
            else:
                r_ds_on_candidates.append(r_ds_on)
                f_sw_candidates.append(best_f_sw)

        return (r_ds_on_candidates, f_sw_candidates)

    fig = plt.figure()
    ax = fig.add_subplot()
    worst_max_fs = 1_000_000
    worst_op = None
    for name, v_in, i_in, v_out in operating_points:
        r_ds_on_candidates, f_sw_candidates = maximize_f_sw_tau(
            v_in, i_in, v_out, tau, p_sw_bud, r_l
        )
        max_fs = max(f_sw_candidates)
        if worst_max_fs > max_fs:
            worst_max_fs = max_fs
            worst_op = name

        ax.plot(r_ds_on_candidates, f_sw_candidates, label=name)

    ax.legend()
    ax.set_title(f"Max Freq vs R_DS_ON for tau={tau * 10**12 :.3f} ps")
    ax.set_xlabel("R_DS_ON (Ohm)")
    ax.set_ylabel("Switching Frequency (Hz)")
    ax.grid()

    plt.tight_layout()
    plt.savefig("fom_f_sw_map.png")
    plt.show()

    return (worst_op, worst_max_fs)


def get_switch_op_fs_map(
    v_in_range, v_out_range, r_ds_on, c_oss, p_sw_bud, r_l, model, num_cells
):
    """_summary_
    Generate a map across all operating points determining upper bound F_SW for
    a given power budget and inductor ripple.

    Args:
        v_in_range ([float]]): Input voltage range in format [min, best, max]
        v_out_range ([float]): Output voltage range in format [min, avg, max]
        r_ds_on (float): Switch on resistance between drain and source
        c_oss (float): Switch output capacitance
        p_sw_bud (float): Maximum budget for switch loss
        r_l (float): Inductor current ripple
        model (func): Solar cell model
        num_cells (int): Number of solar cells

    Returns:
        float: Worst case switching frequency.
    """
    x_v_in = []
    y_v_out = []
    z_f_s = []

    v_in_combos = np.linspace(v_in_range[0], v_in_range[2], num=25, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[2], num=25, endpoint=True)
    for v_in in v_in_combos:
        i_in = model(1000, 298.15, 0, 100, v_in / num_cells)
        for v_out in v_out_combos:
            f_sw, _, _, _ = maximize_f_sw(
                v_in, i_in, v_out, r_ds_on, c_oss, p_sw_bud, r_l
            )
            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_f_s.append(f_sw * 10**-3)

    fig = plt.figure()
    ax = fig.add_subplot()

    # Plot out switching frequency map.
    ax = fig.add_subplot(projection="3d")
    ax.scatter(x_v_in, y_v_out, z_f_s, c=z_f_s)
    ax.set_title("Max Frequency within Power Budget Across I/O Mapping")
    ax.set_xlabel("V_IN (V)")
    ax.set_ylabel("V_OUT (V)")
    ax.set_zlabel("F_S_MAX (kHz)")

    plt.tight_layout()
    plt.savefig("frequency_operation_map.png")
    plt.show()

    return m.floor(min(z_f_s))


def get_switch_duty_cycle_map(v_in_range, v_out_range, eff):
    """_summary_
    Generate a map across all operating points determining duty cycle for


    Args:
        v_in_range ([float]]): Input voltage range in format [min, best, max]
        v_out_range ([float]): Output voltage range in format [min, avg, max]
        eff (float): Efficiency of converter. According TI AN SLVA372D, The
            efficiency is added to the duty cycle calculation, because the
            converter has to deliver also the energy dissipated. This
            calculation gives a more realistic duty cycle than just the equation
            without the efficiency factor.

    Returns:
        (float, float): Minimum and maximum duty cycle required to run the
            converter for all operating points.
    """

    x_v_in = []
    y_v_out = []
    z_duty = []
    for v_in in np.linspace(v_in_range[0], v_in_range[2], num=50, endpoint=True):
        for v_out in np.linspace(v_out_range[0], v_out_range[2], num=50, endpoint=True):
            duty = 1 - v_in * eff / v_out
            x_v_in.append(v_in)
            y_v_out.append(v_out)
            z_duty.append(duty)

    # Plot out switching frequency map.
    fig = plt.figure()
    ax_duty = fig.add_subplot(projection="3d")
    ax_duty.scatter(x_v_in, y_v_out, z_duty, c=z_duty)
    ax_duty.set_title("Minimum Duty Cycle Across I/O Mapping")
    ax_duty.set_xlabel("V_IN (V)")
    ax_duty.set_ylabel("V_OUT (V)")
    ax_duty.set_zlabel("Duty Cycle")

    plt.tight_layout()
    plt.savefig("duty_cycle_operation_map.png")
    plt.show()

    min_duty = np.min(z_duty)
    max_duty = np.max(z_duty)

    return (min_duty, max_duty)
