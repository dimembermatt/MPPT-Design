"""_summary_
@file       switch_design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate design parameters of switches for a DC-DC boost converter.
@version    0.1.0
@date       2023-04-30
"""

import logging
import math as m

import matplotlib.pyplot as plt
import numpy as np

import design_procedures.thermal_design as thermals


def get_requirements(max_v_out, max_i_in, max_p, sf=1.00, eff_dist=0.01):
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

    return (loss_con, loss_swi, loss_tot)


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


def get_rdson_vs_fsw_map(tau, operating_points, p_sw_bud, r_l):
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

    def maximize_fsw_tau(v_in, i_in, v_out, tau, p_sw_bud, r_l):
        candidates = []
        for r_ds_on in list(np.linspace(1e-3, 5e-2, 150)):  # 1mOhm to 50mOhm
            c_oss = tau / r_ds_on
            f_sw, _, _, p_tot = maximize_fsw(
                v_in, i_in, v_out, r_ds_on, c_oss, p_sw_bud, r_l
            )
            if f_sw == 1:
                break
            else:
                candidates.append([r_ds_on, f_sw, p_tot])

        return candidates

    fig, axs = plt.subplots(1, 1)
    fig.suptitle(f"Max Freq vs R_DS_ON for tau={tau * 1E12 :.3f} ps")

    worst_max_fs = 1_000_000
    worst_max_rds_on = None
    worst_op = None
    for name, v_in, i_in, v_out in operating_points:
        candidates = maximize_fsw_tau(v_in, i_in, v_out, tau, p_sw_bud, r_l)
        if len(candidates) == 0:
            return (worst_op, worst_max_fs)

        candidates = np.transpose(candidates)
        r_ds_on_candidates = candidates[0]
        f_sw_candidates = candidates[1]

        f_sw_max = max(f_sw_candidates)
        r_ds_on_max = r_ds_on_candidates[list(f_sw_candidates).index(f_sw_max)]
        if worst_max_fs > f_sw_max:
            worst_max_fs = f_sw_max
            worst_max_rds_on = r_ds_on_max
            worst_op = name

        axs.plot(
            np.multiply(r_ds_on_candidates, 1e3),
            np.divide(f_sw_candidates, 1e3),
            label=name,
        )
        axs.legend()
        axs.set_xlabel("R_DS_ON (mOhm)")
        axs.set_ylabel("Switching Frequency (kHz)")
        axs.grid()

        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(
            arrowstyle="->",
        )
        kw = dict(xycoords="data", arrowprops=arrowprops, bbox=bbox_props)
        axs.annotate(
            "{:.3f}, {:.3f}".format(r_ds_on_max * 1e3, f_sw_max / 1e3),
            xy=(r_ds_on_max * 1e3, f_sw_max / 1e3),
            xytext=(0, 20),
            textcoords="offset points",
            ha="center",
            **kw,
        )

    plt.tight_layout()
    plt.savefig("./outputs/fom_f_sw_map.png")
    plt.close()

    return worst_op, worst_max_fs, worst_max_rds_on


def get_switch_op_fs_map(
    operating_points,
    r_ds_on,
    c_oss,
    p_sw_bud,
    r_l,
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
    points = np.transpose(
        [
            [maximize_fsw(vi, ii, vo, r_ds_on, c_oss, p_sw_bud, r_l), vi, vo]
            for (vi, ii, vo, _) in operating_points
        ]
    )

    # Plot out switching frequency map.
    fig, ax = plt.subplots(1, 1, subplot_kw={"projection": "3d"})
    fig.suptitle(f"Max Freq. Within Power Budget Across I/O Mapping")
    ax.scatter(
        points[1], points[2], np.divide(points[0], 1e3), c=np.divide(points[0], 1e3)
    )
    ax.set_xlabel("V_IN (V)")
    ax.set_ylabel("V_OUT (V)")
    ax.set_zlabel("F_SW_MAX (kHz)")
    ax.view_init(30, 120)
    plt.tight_layout()
    plt.savefig("./outputs/f_sw_map.png")
    plt.close()


def optimize_switches(design, switches, iteration=0):
    source = design["input_source"]
    sink = design["output_sink"]
    sw = design["switches"]
    ind = design["inductor"]
    eff = design["efficiency"]
    map = design["map"]
    sf = design["safety_factor"]

    # Determine switch requirements
    (v_ds_min, i_d_min, p_sw_min, p_sw_bud) = get_requirements(
        sink["upper_bound_voltage"],
        source["upper_bound_current"],
        map["pow"][1][4],
        sf,
        (1 - eff["target_eff"]) * eff["dist"]["sw1"],
    )

    logging.info(
        f"Switch requirements:"
        f"\n\tSwitch V_DS_MIN: {v_ds_min} V"
        f"\n\tSwitch I_D_MIN: {i_d_min} A"
        f"\n\tSwitch P_DISS_MIN: {p_sw_min} W"
        f"\n\tSwitch P_DISS_BUDGET: {p_sw_bud} W")

    # Switch parametric search and filter
    switches_filt = switches[
        (switches["V_DS (V)"] > v_ds_min)
        & (switches["I_D (A)"] > i_d_min)
        & (switches["P_D (W)"] > p_sw_min)
    ]

    # For each switch, determine the optimal F_SW_MIN. The worst case FOM is at
    # input min -> output max.
    worst_case = map["duty"][1]

    def get_f_sw_min(switch):
        r_ds_on = switch["R_DS_ON (mO)"] / 1e3
        c_oss = switch["C_OSS (pF)"] / 1e12
        best_f_sw = maximize_fsw(
            worst_case[0],
            worst_case[1],
            worst_case[2],
            r_ds_on,
            c_oss,
            p_sw_bud,
            ind["r_l"],
        )
        return best_f_sw

    switches_filt = switches_filt.copy()
    switches_filt["F_SW_MIN (Hz)"] = switches_filt.apply(
        lambda switch: get_f_sw_min(switch), axis=1
    )

    # Pick the best switch.
    optimal_sw = switches_filt.nlargest(1, "F_SW_MIN (Hz)")
    logging.info(f"Optimal switch: {optimal_sw}")

    # Limit max switching frequency.
    if optimal_sw.iloc[0]["F_SW_MIN (Hz)"] > sw["max_f_sw"]:
        optimal_sw.iloc[0]["F_SW_MIN (Hz)"] = sw["max_f_sw"]
    sw["f_sw"] = optimal_sw.iloc[0]["F_SW_MIN (Hz)"]

    # Plot F_SW_MIN vs IO map.
    get_switch_op_fs_map(
        map["points"],
        optimal_sw.iloc[0]["R_DS_ON (mO)"] * 1e-3,
        optimal_sw.iloc[0]["C_OSS (pF)"] * 1e-12,
        p_sw_bud,
        ind["r_l"],
    )

    # Determine switch losses at best case.
    best_case = map["duty"][0]
    p_cond, p_sw, p_tot = get_losses(
        best_case[0],
        best_case[1],
        best_case[2],
        optimal_sw.iloc[0]["F_SW_MIN (Hz)"],
        optimal_sw.iloc[0]["R_DS_ON (mO)"] * 1e-3,
        optimal_sw.iloc[0]["C_OSS (pF)"] * 1e-12,
        ind["r_l"],
    )

    logging.info(
        f"Switch losses in best case: {p_cond :.3f}, {p_sw :.3f}, {p_tot :.3f} W"
    )

    # Determine switch losses at worst case.
    worst_case = map["duty"][1]
    p_cond, p_sw, p_tot = get_losses(
        worst_case[0],
        worst_case[1],
        worst_case[2],
        optimal_sw.iloc[0]["F_SW_MIN (Hz)"],
        optimal_sw.iloc[0]["R_DS_ON (mO)"] * 1e-3,
        optimal_sw.iloc[0]["C_OSS (pF)"] * 1e-12,
        ind["r_l"],
    )

    logging.info(
        f"Switch losses in worst case: {p_cond :.3f}, {p_sw :.3f}, {p_tot :.3f} W"
    )

    # Determine switch thermals.
    t_amb = 60
    t_max = list(optimal_sw["T_J_MAX (C)"])[0] * (1 / sf)
    therm_area = thermals.get_switch_thermals(
        t_amb,  # STC
        t_max,
        p_sw_bud,
        list(optimal_sw["R_JB (C/W)"])[0],
        list(optimal_sw["R_JC (C/W)"])[0],
        0.0,
        0.1 * 1e-6,  # small
        # design["exposed_thermal_area (mm^2)"] * 1e-6,
        100,  # Assume at least 100 vias
    )

    logging.info(
        f"Minimum required thermal area per switch to dissipate {p_sw_bud :.3f}W of heat from {t_amb} C to "
        f"{t_max} C: {therm_area * 10000 :.3f} cm^2 ({therm_area * 1000000 :.3f} mm^2)."
    )

    # Losses in worst case.
    return p_tot
