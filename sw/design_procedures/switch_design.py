"""_summary_
@file       switch_design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate design parameters of switches for a DC-DC boost converter.
@version    1.0.0
@date       2023-05-06
@file_overview
    optimize_switches
        get_switch_requirements
            v_ds_min
            i_d_min
            p_d_min

        get_optimal_switch
            filter switches based on requirements
            maximize_fsw
                get_losses

            best switch candidate

        get_worst_case_losses

        returns chosen switches, loss vs budget

    map_switches
        map_switch_losses
            get_losses
        map_switch_thermals
            get_switch_thermals
        map_switch_deadtime
            get_switch_deadtime
"""

import logging
import math as m

import design_procedures.thermal_design as thermals
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def get_requirements(max_v_out, max_i_in, p_bud, sf=1.00):
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
    p_sw_min = p_bud * sf
    p_sw_bud = p_bud

    return v_ds_min, i_ds_min, p_sw_min, p_sw_bud


def get_losses(v_in, i_in, v_out, f_sw, r_ds_on, c_oss, r_l):
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

    return loss_con, loss_swi, loss_tot


def maximize_fsw(v_in, i_in, v_out, r_ds_on, c_oss, p_sw_bud, r_l):
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
    best_f_sw = 5000
    while True:
        new_f_sw = best_f_sw + 5000
        _, _, p_total = get_losses(v_in, i_in, v_out, new_f_sw, r_ds_on, c_oss, r_l)
        if p_total > p_sw_bud:
            break
        else:
            best_f_sw = new_f_sw
    return best_f_sw


def get_optimal_switch(switches, v_ds_min, i_d_min, p_min, p_bud, worst_case, r_l):
    # Filter switches based on requirements
    switches_filt = switches[
        (switches["V_DS (V)"] > v_ds_min)
        & (switches["I_D (A)"] > i_d_min)
        & (switches["P_D (W)"] > p_min)
    ]

    # Maximize f_sw for each switch
    def get_best_fsw(switch):
        r_ds_on = switch["R_DS_ON (mO)"] / 1e3
        c_oss = switch["C_OSS (pF)"] / 1e12
        best_f_sw = maximize_fsw(
            worst_case.iloc[0]["VI (V)"],
            worst_case.iloc[0]["II (A)"],
            worst_case.iloc[0]["VO (V)"],
            r_ds_on,
            c_oss,
            p_bud,
            r_l,
        )
        return best_f_sw

    switches_filt = switches_filt.copy()
    switches_filt["F_SW_MIN (Hz)"] = switches_filt.apply(
        lambda switch: get_best_fsw(switch), axis=1
    )

    # Pick the switch with the highest lower bound F_SW
    optimal_switch = switches_filt.nlargest(1, "F_SW_MIN (Hz)")
    return optimal_switch


def optimize_switches(design, switches):
    sw = design["switches"]
    ind = design["inductor"]
    map = design["map"]
    sf = design["safety_factor"]

    # Get switch requirements
    v_ds_min, i_d_min, p_min, p_bud = get_requirements(
        map["out_vol"][1],
        map["inp_cur"][1],
        sw["p_bud"],
        sf,
    )

    logging.info(
        f"Switch requirements:"
        f"\n\tV_DS >= {v_ds_min :.3f} (V)"
        f"\n\tI_D >= {i_d_min :.3f} (A)"
        f"\n\tP_D >= {p_min :.3f} (W)"
    )

    worst_case = map["points"][map["points"]["DUTY (%)"] == map["duty"][1]]

    # Get optimal switch
    optimal_switch = get_optimal_switch(
        switches, v_ds_min, i_d_min, p_min, p_bud, worst_case, ind["r_l"]
    )

    # Get worst case losses
    p_cond, p_sw, p_loss = get_losses(
        worst_case.iloc[0]["VI (V)"],
        worst_case.iloc[0]["II (A)"],
        worst_case.iloc[0]["VO (V)"],
        optimal_switch.iloc[0]["F_SW_MIN (Hz)"],
        optimal_switch.iloc[0]["R_DS_ON (mO)"] * 1e-3,
        optimal_switch.iloc[0]["C_OSS (pF)"] * 1e-12,
        ind["r_l"],
    )

    sw["f_sw"] = optimal_switch.iloc[0]["F_SW_MIN (Hz)"]

    logging.info(
        f"Switch selected:"
        f"\n\t{optimal_switch.iloc[0]['PART_NAME']}"
        f"\n\twith an optimal switching frequency of {sw['f_sw']} Hz"
    )

    return optimal_switch, p_loss


def get_switch_deadtime(coss, vi, ii, vo, r_l):
    pi = vi * ii
    return 2 * coss * vi * vo / (pi * (1 + r_l))


def map_switch_deadtime(switch, points, r_l, output_path):
    c_oss = switch.iloc[0]["C_OSS (pF)"] * 1e-12

    def _get_switch_deadtime(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        return get_switch_deadtime(c_oss, vi, ii, vo, r_l) * 1e9

    points["T_DEAD (ns)"] = points.apply(_get_switch_deadtime, axis=1)

    # Plot out switching frequency map.
    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Min Deadtime Across I/O Map")
    ax.scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["T_DEAD (ns)"],
        c=points["T_DEAD (ns)"],
    )
    ax.set_xlabel("$V_{IN}$ (V)")
    ax.set_ylabel("$V_{OUT}$ (V)")
    ax.set_zlabel("$T_{D}$ (ns)")
    ax.view_init(30, -45)
    plt.tight_layout()
    plt.show()
    fig.savefig(output_path + "/07_sw_deadtime_map.png")
    plt.close()

    logging.info(f"Worst case deadtime:" f"\n\t{np.max(points['T_DEAD (ns)']) :.3f} ns")

    return points


def map_switch_thermals(switch, sf, p_loss, output_path):
    t_amb = 60
    t_max = switch.iloc[0]["T_J_MAX (C)"] * (1 / sf)
    therm_area = thermals.get_switch_thermals(
        t_amb,  # STC
        t_max,
        p_loss * 2,
        switch.iloc[0]["R_JB (C/W)"],
        switch.iloc[0]["R_JC (C/W)"],
        0.0,
        0.1 * 1e-0,  # small
        # design["exposed_thermal_area (mm^2)"] * 1e-6,
        100,  # Assume at least 100 vias
        output_path,
    )

    logging.info(
        f"Best case thermal area for both switches:"
        f"\n\t{therm_area * 10000 :.3f} cm^2"
    )


def map_switch_losses(switch, points, f_sw, r_l, output_path):
    c_oss = switch.iloc[0]["C_OSS (pF)"] * 1e-12
    r_ds_on = switch.iloc[0]["R_DS_ON (mO)"] * 1e-3

    def _get_losses(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        return pd.Series(get_losses(vi, ii, vo, f_sw, r_ds_on, c_oss, r_l))

    points[["PSW_COND (W)", "PSW_SW (W)", "PSW_TOT (W)"]] = points.apply(
        _get_losses, axis=1
    )

    # Plot out loss map.
    fig, axs = plt.subplots(1, 3, subplot_kw={"projection": "3d"})
    fig.suptitle("Switching Losses Per Switch Across I/O Map")
    axs[0].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PSW_COND (W)"],
        c=points["PSW_COND (W)"],
    )
    axs[0].set_title("Conduction Loss")
    axs[0].set_xlabel("$V_{IN}$ (V)")
    axs[0].set_ylabel("$V_{OUT}$ (V)")
    axs[0].set_zlabel("$P_{COND}$ (W)")

    axs[1].scatter(
        points["VI (V)"], points["VO (V)"], points["PSW_SW (W)"], c=points["PSW_SW (W)"]
    )
    axs[1].set_title("Switching Loss")
    axs[1].set_xlabel("$V_{IN}$ (V)")
    axs[1].set_ylabel("$V_{OUT}$ (V)")
    axs[1].set_zlabel("$P_{SW}$ (W)")

    axs[2].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PSW_TOT (W)"],
        c=points["PSW_TOT (W)"],
    )
    axs[2].set_title("Total Loss")
    axs[2].set_xlabel("$V_{IN}$ (V)")
    axs[2].set_ylabel("$V_{OUT}$ (V)")
    axs[2].set_zlabel("$P_{TOT}$ (W)")

    fig.set_size_inches(12, 5)
    plt.tight_layout()
    plt.subplots_adjust(right=0.94, wspace=0.15)
    plt.show()
    fig.savefig(output_path + "/05_sw_losses_map.png")
    plt.close()

    logging.info(
        f"Worst case conduction, switching, and total loss:"
        f"\n\tConduction loss: {np.max(points['PSW_COND (W)']) :.3f} W"
        f"\n\tSwitching loss: {np.max(points['PSW_SW (W)']) :.3f} W"
        f"\n\tTotal loss: {np.max(points['PSW_TOT (W)']) :.3f} W"
    )

    return points


def map_switches(design, switch, output_path):
    sw = design["switches"]
    ind = design["inductor"]
    map = design["map"]
    sf = design["safety_factor"]

    points = map["points"]
    f_sw = sw["f_sw"]
    r_l = ind["r_l"]

    points = map_switch_losses(switch, points, f_sw, r_l, output_path)
    p_loss = np.max(points["PSW_TOT (W)"])
    map_switch_thermals(switch, sf, p_loss, output_path)
    points = map_switch_deadtime(switch, points, r_l, output_path)
    return points
