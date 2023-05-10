    def plot(points):
        # Plot out passive characteristics map.
        fig, axs = plt.subplots(3, 3, subplot_kw=dict(projection="3d"))
        axs[0, 0].scatter(
            points[0], points[1], np.multiply(points[2], 1e6), c=points[2]
        )
        axs[0, 0].set_title("Min. $C_{I}$ Across I/O Mapping")
        axs[0, 0].set_xlabel("$V_{IN}$ (V)")
        axs[0, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 0].set_zlabel("Capacitance (uF)")

        axs[1, 0].scatter(points[0], points[1], points[3], c=points[3])
        axs[1, 0].set_title("Max. $V_{CI,PKPK}$ Across I/O Mapping")
        axs[1, 0].set_xlabel("$V_{IN}$ (V)")
        axs[1, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 0].set_zlabel("$V_{PKPK}$ (V)")

        axs[2, 0].scatter(points[0], points[1], points[4], c=points[4])
        axs[2, 0].set_title("Max. $V_{CI}$ Across I/O Mapping")
        axs[2, 0].set_xlabel("$V_{IN}$ (V)")
        axs[2, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 0].set_zlabel("$V_{MAX}$ (V)")
    def plot(points):
        # Plot out passive characteristics map.
        fig, axs = plt.subplots(3, 3, subplot_kw=dict(projection="3d"))
        axs[0, 0].scatter(
            points[0], points[1], np.multiply(points[2], 1e6), c=points[2]
        )
        axs[0, 0].set_title("Min. $C_{I}$ Across I/O Mapping")
        axs[0, 0].set_xlabel("$V_{IN}$ (V)")
        axs[0, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 0].set_zlabel("Capacitance (uF)")

        axs[1, 0].scatter(points[0], points[1], points[3], c=points[3])
        axs[1, 0].set_title("Max. $V_{CI,PKPK}$ Across I/O Mapping")
        axs[1, 0].set_xlabel("$V_{IN}$ (V)")
        axs[1, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 0].set_zlabel("$V_{PKPK}$ (V)")

        axs[2, 0].scatter(points[0], points[1], points[4], c=points[4])
        axs[2, 0].set_title("Max. $V_{CI}$ Across I/O Mapping")
        axs[2, 0].set_xlabel("$V_{IN}$ (V)")
        axs[2, 0].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 0].set_zlabel("$V_{MAX}$ (V)")

        axs[0, 1].scatter(
            points[0], points[1], np.multiply(points[5], 1e6), c=points[5]
        )
        axs[0, 1].set_title("Min. $C_{O}$ Across I/O Mapping")
        axs[0, 1].set_xlabel("$V_{IN}$ (V)")
        axs[0, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 1].set_zlabel("Capacitance (uF)")

        axs[1, 1].scatter(points[0], points[1], points[6], c=points[6])
        axs[1, 1].set_title("Max. $V_{CO,PKPK}$ Across I/O Mapping")
        axs[1, 1].set_xlabel("$V_{IN}$ (V)")
        axs[1, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 1].set_zlabel("$V_{PKPK}$ (V)")

        axs[2, 1].scatter(points[0], points[1], points[7], c=points[7])
        axs[2, 1].set_title("Max. $V_{CO}$ Across I/O Mapping")
        axs[2, 1].set_xlabel("$V_{IN}$ (V)")
        axs[2, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 1].set_zlabel("$V_{MAX}$ (V)")

        axs[0, 2].scatter(
            points[0], points[1], np.multiply(points[8], 1e6), c=points[8]
        )
        axs[0, 2].set_title("Min. L Across I/O Mapping")
        axs[0, 2].set_xlabel("$V_{IN}$ (V)")
        axs[0, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 2].set_zlabel("Inductance (uH)")

        axs[1, 2].scatter(points[0], points[1], points[9], c=points[9])
        axs[1, 2].set_title("Max. $I_{L,PKPK}$ Across I/O Mapping")
        axs[1, 2].set_xlabel("$V_{IN}$ (V)")
        axs[1, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 2].set_zlabel("$I_{PKPK}$ (A)")

        axs[2, 2].scatter(points[0], points[1], points[10], c=points[10])
        axs[2, 2].set_title("Max. $I_{L}$ Across I/O Mapping")
        axs[2, 2].set_xlabel("$V_{IN}$ (V)")
        axs[2, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 2].set_zlabel("$I_{MAX}$ (A)")

        fig.set_size_inches(11, 10)
        plt.tight_layout()
        plt.savefig("./outputs/passive_sizing_map.png")
        plt.close()

        axs[0, 1].scatter(
            points[0], points[1], np.multiply(points[5], 1e6), c=points[5]
        )
        axs[0, 1].set_title("Min. $C_{O}$ Across I/O Mapping")
        axs[0, 1].set_xlabel("$V_{IN}$ (V)")
        axs[0, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 1].set_zlabel("Capacitance (uF)")

        axs[1, 1].scatter(points[0], points[1], points[6], c=points[6])
        axs[1, 1].set_title("Max. $V_{CO,PKPK}$ Across I/O Mapping")
        axs[1, 1].set_xlabel("$V_{IN}$ (V)")
        axs[1, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 1].set_zlabel("$V_{PKPK}$ (V)")

        axs[2, 1].scatter(points[0], points[1], points[7], c=points[7])
        axs[2, 1].set_title("Max. $V_{CO}$ Across I/O Mapping")
        axs[2, 1].set_xlabel("$V_{IN}$ (V)")
        axs[2, 1].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 1].set_zlabel("$V_{MAX}$ (V)")

        axs[0, 2].scatter(
            points[0], points[1], np.multiply(points[8], 1e6), c=points[8]
        )
        axs[0, 2].set_title("Min. L Across I/O Mapping")
        axs[0, 2].set_xlabel("$V_{IN}$ (V)")
        axs[0, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[0, 2].set_zlabel("Inductance (uH)")

        axs[1, 2].scatter(points[0], points[1], points[9], c=points[9])
        axs[1, 2].set_title("Max. $I_{L,PKPK}$ Across I/O Mapping")
        axs[1, 2].set_xlabel("$V_{IN}$ (V)")
        axs[1, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[1, 2].set_zlabel("$I_{PKPK}$ (A)")

        axs[2, 2].scatter(points[0], points[1], points[10], c=points[10])
        axs[2, 2].set_title("Max. $I_{L}$ Across I/O Mapping")
        axs[2, 2].set_xlabel("$V_{IN}$ (V)")
        axs[2, 2].set_ylabel("$V_{OUT}$ (V)")
        axs[2, 2].set_zlabel("$I_{MAX}$ (A)")

        fig.set_size_inches(11, 10)
        plt.tight_layout()
        plt.savefig("./outputs/passive_sizing_map.png")
        plt.close()




def optimize_passives(design, capacitors, inductors, iteration=0):
    source = design["input_source"]
    sink = design["output_sink"]
    sw = design["switches"]
    ci = design["input_cap"]
    co = design["output_cap"]
    ind = design["inductor"]
    eff = design["efficiency"]
    map = design["map"]
    sf = design["safety_factor"]

    # Determine capacitor and inductor requirements
    (
        ci_min,
        ci_v_pkpk,
        ci_v_min,
        co_min,
        co_v_pkpk,
        co_v_min,
        l_min,
        l_i_pkpk,
        l_i_min,
    ) = get_requirements(
        map["points"],
        sw["f_sw"],
        ci["v_pk_pk"],
        co["v_pk_pk"],
        ind["r_l"],
        sf=sf,
    )

    logging.info(
        f"Capacitor requirements:"
        f"\n\tInput Capacitor C_MIN: {ci_min * 1e6 :.3f} uF"
        f"\n\tInput Capacitor V_D_MIN: {ci_v_min} V"
        f"\n\tOutput Capacitor C_MIN: {co_min * 1e6 :.3f} uF"
        f"\n\tOutput Capacitor V_D_MIN: {co_v_min} V"
        f"\nInductor requirements:"
        f"\n\tInductor L_MIN: {l_min * 1e6 :.3f} uH"
        f"\n\tInductor I_L_MIN: {l_i_min} A"
    )

    # Capture electrolytic capacitors, generate power dissipation requirements.
    capacitors_electrolytic = capacitors[
        (capacitors["Capacitor Type"] == "Electrolytic")
    ]

    capacitors_electrolytic = capacitors_electrolytic.copy()
    capacitors_electrolytic["P_IN_DISS (W)"] = capacitors_electrolytic.apply(
        lambda capacitor: get_capacitor_pow_diss(
            get_capacitor_i_rms(l_i_pkpk),
            capacitor["ESR (mO)"] * 1e-3,
            capacitor["LEAKAGE (uA)"] * 1e-6,
            ci_v_min,
        ),
        axis=1,
    )
    capacitors_electrolytic["P_OUT_DISS (W)"] = capacitors_electrolytic.apply(
        lambda capacitor: get_capacitor_pow_diss(
            get_capacitor_i_rms(l_i_pkpk),
            capacitor["ESR (mO)"] * 1e-3,
            capacitor["LEAKAGE (uA)"] * 1e-6,
            co_v_min,
        ),
        axis=1,
    )

    logging.info(capacitors_electrolytic)

    # Find the combination of electrolytics to meet bulk capacitance at lowest
    # power dissipation.
    bulk_in_capacitors = get_bulk_capacitance(
        capacitors_electrolytic, ci_v_min, ci_min, l_i_pkpk, "P_IN_DISS (W)"
    )
    ci = np.sum([c for (_, c, _, _) in bulk_in_capacitors])
    ii = np.sum([i for (_, _, i, _) in bulk_in_capacitors])
    pi = np.sum([p for (_, _, _, p) in bulk_in_capacitors])

    bulk_out_capacitors = get_bulk_capacitance(
        capacitors_electrolytic, co_v_min, co_min, l_i_pkpk, "P_OUT_DISS (W)"
    )
    co = np.sum([c for (_, c, _, _) in bulk_out_capacitors])
    io = np.sum([i for (_, _, i, _) in bulk_out_capacitors])
    po = np.sum([p for (_, _, _, p) in bulk_out_capacitors])

    logging.info(
        f"Input bulk capacitors:"
        f"\n\t[{ci :.3f} uF | {ii :.3f} mA | {pi * 1e3 :.3f} mW]"
        f"\n\t{bulk_in_capacitors}"
        f"\nOutput bulk capacitors:"
        f"\n\t[{co :.3f} uF | {io :.3f} mA | {po * 1e3 :.3f} mW]"
        f"\n\t{bulk_out_capacitors}"
    )

    # TODO: Capture MLCC capacitors, generate power dissipation requirements

    # Find a suitable MLCC based on ...

    # Inductor parametric search and filter

    return pi, po, 0.0




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







if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    # i_mpp = 7
    # r_l_a = 2.5  # A
    # r_l = r_l_a / i_mpp / 2
    # i_max = (i_mpp + r_l_a)  # A

    # l = 100 * 1e-6  # uH
    # b_sat = 375 * 1e-3  # T

    # (k_g_target, k_g, b_ac, N, A_w, l_w, r, p_cond) = get_inductor_sizing(
    #     l, i_max, b_sat, r_l
    # )

    # print(r_l, i_max, N, p_cond)

    # p_v = 15  # kW/m^3
    # p_core = get_inductor_core_loss(p_v)
    # print(p_core)

    # 1.25 A (10%), 300 uH -> i_max=7.77, N=82, PCOND=16
    # 1.75 A (14.2%), 300 uH -> i_max=8.3, N=88, PCOND=21
    # 1.25 A (10%), 200 uH -> i_max=7.77, N=55, PCOND=7.25
    # 1.75 A (14.2%), 200 uH -> i_max=8.3, N=59, PCOND=9.5
    # 2 A (16.2%), 150 uH -> i_max=8.56, N=45, PCOND=5.9
    # 2.25 A (18.3%), 125 uH -> i_max=8.82, N=39, PCOND=4.7
    # 2.5 A (20.3%), 100 uH -> i_max=9.01, N=32, PCOND=3.35

    # Cap test
    # c = 1.034 * 1E-6 # uF
    # df = 2.5 / 100 # %
    # f_sw = 104 * 1E3 # kHz
    # v_max = 250

    # esr = get_capacitor_esr(c, f_sw, df) # ohms
    # esr = 5.4 * 1E-3 # mO
    # print(f"{esr * 1E3} mO")

    # z = get_capacitor_impedance(c, f_sw)
    # v_rms = get_capacitor_v_rms(v_max)
    # i_rms = get_capacitor_i_rms(v_rms, z)
    # i_rms = 2.75 # A

    # print(f"Imp: {z}")
    # print(f"V_RMS: {v_rms} V, I_RMS: {i_rms} A")

    inductor_current_pk_pk = 2.75  # A
    i_rms = inductor_current_pk_pk / (2 * m.sqrt(2))
    print(f"I_RMS: {i_rms} A")

    # Input cap
    # 80-A759KS156M2AAAE52
    c = 15 * 1e-6  # uF
    esr = 52 * 1e-3  # mO
    p_dis = get_capacitor_pow_diss(i_rms, esr)
    print(f"P_DIS: {p_dis} W")

    # Output cap
    # 810-CGA9P3X7T2E225MA
    # @ 125 V bias, 125 C, 109 kHz
    c = 1.034 * 1e-6  # uF
    esr = 5.4 * 1e-3  # mO
    p_dis = get_capacitor_pow_diss(i_rms, esr)
    print(f"P_DIS: {p_dis} W")

    # 80-A759MS186M2CAAE90 * 2
    c = 36 * 1e-6  # uF
    esr = 45 * 1e-3  # mO
    p_dis = get_capacitor_pow_diss(i_rms, esr)
    print(f"P_DIS: {p_dis} W")




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
        f"\n\tSwitch P_DISS_BUDGET: {p_sw_bud} W"
    )

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
    return p_tot, p_sw_bud



def get_passive_sizing(operating_points, f_sw, r_ci_v, r_co_v, r_l_a, eff, sf=0.25):
    """_summary_
    Generat map of passive requirements for operation at various operating points.

    Args:
        v_in_range ([float]]): Input voltage range in format [min, best, max]
        v_out_range ([float]): Output voltage range in format [min, avg, max]
        f_sw (float): Switching frequency
        r_ci_v (float): Maximum allowed input capacitor voltage ripple
        r_co_v (float): Maximum allowed output capacitor voltage ripple
        r_l_a (float): Maximum allowed inductor current ripple
        eff (float): System efficiency
        model (func): Solar cell model
        num_cells (int): Number of solar cells
        sf (float, optional): Safety factor. Defaults to 0.25.

    Returns:
        (float, ...): Set of floats consisting of:
            Minimum input capacitance
            Minimum output capacitance
            Minimum inductance
            Minimum VDC for input capacitor
            Minimum VDC for output capacitor
            Minimum I_D for inductor
    """

    # Given that the PV is a nonlinear current source, it's not directly
    # straightforward to determine when ci, co, l are minimized. We do know,
    # however, that the minimum feasible passive value is bounded by the worst
    # input/output combo.
    ci_min = []
    co_min = []
    l_min = []
    i_l_max = []
    v_ci_max = []
    v_co_max = []

    x_v_in = []
    y_v_out = []

    for (v_in, i_in, v_out, i_out) in operating_points:
        p_in = v_in * i_in
        x_v_in.append(v_in)
        y_v_out.append(v_out)

        # ci = (r_l * i_in) / (8 * r_ci * v_out * f_sw)
        # co = (v_out - v_in) * p_in / (2 * r_co * v_out**3 * f_sw)

        i_out = p_in / v_out

        duty = 1 - v_in * eff / v_out
        l = v_in * (v_out - v_in) / (r_l_a * f_sw * v_out)
        r_l_a_op = v_in * duty / (f_sw * l)

        ci = r_l_a_op / (8 * f_sw * r_ci_v)

        co = (p_in / v_out * duty) / (f_sw * r_co_v)
        r_co_v_op = (v_out - v_in) * i_out / (v_out * f_sw * co)

        # print(f"\nI/O: {v_in :.3f}[{i_in :.3f}]/{v_out :.3f}[{i_out :.3f}]")
        # print(f"Duty: {duty :.3f}")
        # print(f"Min inductance: {l * 1E6 :.3f} uH")
        # print(f"Inductor ripple current: {r_l_a_op :.3f} A")

        # print(f"Min inp. cap.: {ci * 1E6 :.3f} uF")
        # print(f"Inp. cap. ripple voltage: {r_ci_v :.3f} V")

        # print(f"Min out. cap.: {co * 1E6 :.3f} uF")
        # print(f"Out. cap. ripple voltage: {r_co_v_op :.3f} V")

        ci_min.append(ci)
        co_min.append(co)
        l_min.append(l)
        i_l_max.append(r_l_a_op)
        v_ci_max.append(r_ci_v)
        v_co_max.append(r_co_v_op)

    def plot():
        # Plot out switching frequency map.
        fig, axs = plt.subplots(2, 3, subplot_kw=dict(projection="3d"))
        axs[0, 0].scatter(x_v_in, y_v_out, np.multiply(ci_min, 1e6), c=ci_min)
        axs[0, 0].set_title("Min. C_I Across I/O Mapping")
        axs[0, 0].set_xlabel("V_IN (V)")
        axs[0, 0].set_ylabel("V_OUT (V)")
        axs[0, 0].set_zlabel("Capacitance (uF)")

        axs[1, 0].scatter(x_v_in, y_v_out, v_ci_max, c=v_ci_max)
        axs[1, 0].set_title("Max. V_CI Across I/O Mapping")
        axs[1, 0].set_xlabel("V_IN (V)")
        axs[1, 0].set_ylabel("V_OUT (V)")
        axs[1, 0].set_zlabel("V_MAX (V)")

        axs[0, 1].scatter(x_v_in, y_v_out, np.multiply(co_min, 1e6), c=co_min)
        axs[0, 1].set_title("Min. C_O Across I/O Mapping")
        axs[0, 1].set_xlabel("V_IN (V)")
        axs[0, 1].set_ylabel("V_OUT (V)")
        axs[0, 1].set_zlabel("Capacitance (uF)")

        axs[1, 1].scatter(x_v_in, y_v_out, v_co_max, c=v_co_max)
        axs[1, 1].set_title("Max. V_CO Across I/O Mapping")
        axs[1, 1].set_xlabel("V_IN (V)")
        axs[1, 1].set_ylabel("V_OUT (V)")
        axs[1, 1].set_zlabel("V_MAX (V)")

        axs[0, 2].scatter(x_v_in, y_v_out, np.multiply(l_min, 1e6), c=l_min)
        axs[0, 2].set_title("Min. L Across I/O Mapping")
        axs[0, 2].set_xlabel("V_IN (V)")
        axs[0, 2].set_ylabel("V_OUT (V)")
        axs[0, 2].set_zlabel("Inductance (uH)")

        axs[1, 2].scatter(x_v_in, y_v_out, i_l_max, c=i_l_max)
        axs[1, 2].set_title("Max. I_L Across I/O Mapping")
        axs[1, 2].set_xlabel("V_IN (V)")
        axs[1, 2].set_ylabel("V_OUT (V)")
        axs[1, 2].set_zlabel("Current (A)")

        plt.tight_layout()
        plt.savefig("capacitor_inductor_sizing_map.png")
        plt.show()

    # Encapsulate so I can fold
    plot()

    ci_min = np.max(ci_min)
    co_min = np.max(co_min)
    l_min = np.max(l_min)

    ci_vdc_min = np.max(v_ci_max) * sf
    co_vdc_min = np.max(v_co_max) * sf
    l_a_min = np.max(i_l_max) * 1.05  # override * sf

    return (ci_min, co_min, l_min, ci_vdc_min, co_vdc_min, l_a_min)


def get_inductor_sizing(l, i_max, b_sat, r_l):
    """_summary_
    Size the inductor.

    Args:
        l (float): Inductance, in H
        i_max (float): Max current, in A
        b_sat (float): Magnetic field saturation, in T
        r_l (float): Inductor current ripple ratio

    Returns:
        (float, ...): Set of floats consisting of:
            Maximum k_g
            Real k_g
            Magnetic field at AC, in T
            Number of turns
            Cross-sectional area of wire, in m^2
            Length of wire, in m^2
            Resistance of wire in Ohms
            Power loss from conduction, in W
    """

    # Assume PQ 26/25, B65877A
    k_g_target = 0.125  # cm^5
    A_c = 0.0001088  # cross sectional area of core, m^2
    A_n = 4.7e-5  # cross sectional area of winding, m^2
    l_n = 0.056  # length of turn, m
    rho = 2 * 1e-8
    k_u = 0.3  # Hand wound packing factor

    # choose b_sat from datasheet
    b_pk = b_sat * 0.75

    # Get number of turns
    N = m.ceil(l * i_max / (b_pk * A_c))

    # Get area of wire
    A_w = A_n * k_u / N

    # Get length of wire
    l_w = l_n * N

    # Get resistance of wire
    r_real = rho * l_w / A_w

    # Get power loss from conduction
    i_rms = i_max / m.sqrt(2)
    p_cond = i_rms**2 * r_real

    # Derive required k_g
    k_g = l**2 * i_max**2 * rho / (b_pk**2 * r_real * k_u) * 1e10

    # Get b_ac for core loss
    b_ac = b_pk * r_l / (1 + r_l)

    return (k_g_target, k_g, b_ac, N, A_w, l_w, r_real, p_cond)


def get_inductor_core_loss(p_v):
    """_summary_
    Get inductor core loss as a function of p_v and volume.

    Args:
        p_v (float): loss, in kW/m^3 as chosen on chart

    Returns:
        float: loss, in W
    """
    vol = 6.54e-6  # m^3
    return p_v * vol * 1e3


def get_capacitor_esr(c, f_sw, df):
    ESR = df / (2 * m.pi * f_sw * c)
    return ESR


def get_capacitor_impedance(c, f_sw):
    return 1 / (2 * m.pi * f_sw * c)


def get_capacitor_v_rms(v_pp):
    return v_pp / (2 * m.sqrt(2))


def get_capacitor_i_rms(v_rms, z):
    return v_rms / z




def get_two_caps_parallel(f_sw, z1, z2):
    c1, r1 = z1
    c2, r2 = z2

    num = (r1 + 1 / (1j * f_sw * c1)) * (r2 + 1 / (1j * f_sw * c2))
    denom = (r1 + 1 / (1j * f_sw * c1)) + (r2 + 1 / (1j * f_sw * c2))
    print(z1, z2)
    print(num, denom)
    return (num / denom).imag, (num / denom).real










def get_passive_sizing(operating_points, f_sw, r_ci_v, r_co_v, r_l_a, eff, sf=0.25):
    """_summary_
    Generat map of passive requirements for operation at various operating points.

    Args:
        v_in_range ([float]]): Input voltage range in format [min, best, max]
        v_out_range ([float]): Output voltage range in format [min, avg, max]
        f_sw (float): Switching frequency
        r_ci_v (float): Maximum allowed input capacitor voltage ripple
        r_co_v (float): Maximum allowed output capacitor voltage ripple
        r_l_a (float): Maximum allowed inductor current ripple
        eff (float): System efficiency
        model (func): Solar cell model
        num_cells (int): Number of solar cells
        sf (float, optional): Safety factor. Defaults to 0.25.

    Returns:
        (float, ...): Set of floats consisting of:
            Minimum input capacitance
            Minimum output capacitance
            Minimum inductance
            Minimum VDC for input capacitor
            Minimum VDC for output capacitor
            Minimum I_D for inductor
    """

    # Given that the PV is a nonlinear current source, it's not directly
    # straightforward to determine when ci, co, l are minimized. We do know,
    # however, that the minimum feasible passive value is bounded by the worst
    # input/output combo.
    ci_min = []
    co_min = []
    l_min = []
    i_l_max = []
    v_ci_max = []
    v_co_max = []

    x_v_in = []
    y_v_out = []

    for (v_in, i_in, v_out, i_out) in operating_points:
        p_in = v_in * i_in
        x_v_in.append(v_in)
        y_v_out.append(v_out)

        # ci = (r_l * i_in) / (8 * r_ci * v_out * f_sw)
        # co = (v_out - v_in) * p_in / (2 * r_co * v_out**3 * f_sw)

        i_out = p_in / v_out

        duty = 1 - v_in * eff / v_out
        l = v_in * (v_out - v_in) / (r_l_a * f_sw * v_out)
        r_l_a_op = v_in * duty / (f_sw * l)

        ci = r_l_a_op / (8 * f_sw * r_ci_v)

        co = (p_in / v_out * duty) / (f_sw * r_co_v)
        r_co_v_op = (v_out - v_in) * i_out / (v_out * f_sw * co)

        # print(f"\nI/O: {v_in :.3f}[{i_in :.3f}]/{v_out :.3f}[{i_out :.3f}]")
        # print(f"Duty: {duty :.3f}")
        # print(f"Min inductance: {l * 1E6 :.3f} uH")
        # print(f"Inductor ripple current: {r_l_a_op :.3f} A")

        # print(f"Min inp. cap.: {ci * 1E6 :.3f} uF")
        # print(f"Inp. cap. ripple voltage: {r_ci_v :.3f} V")

        # print(f"Min out. cap.: {co * 1E6 :.3f} uF")
        # print(f"Out. cap. ripple voltage: {r_co_v_op :.3f} V")

        ci_min.append(ci)
        co_min.append(co)
        l_min.append(l)
        i_l_max.append(r_l_a_op)
        v_ci_max.append(r_ci_v)
        v_co_max.append(r_co_v_op)

    def plot():
        # Plot out switching frequency map.
        fig, axs = plt.subplots(2, 3, subplot_kw=dict(projection="3d"))
        axs[0, 0].scatter(x_v_in, y_v_out, np.multiply(ci_min, 1e6), c=ci_min)
        axs[0, 0].set_title("Min. C_I Across I/O Mapping")
        axs[0, 0].set_xlabel("V_IN (V)")
        axs[0, 0].set_ylabel("V_OUT (V)")
        axs[0, 0].set_zlabel("Capacitance (uF)")

        axs[1, 0].scatter(x_v_in, y_v_out, v_ci_max, c=v_ci_max)
        axs[1, 0].set_title("Max. V_CI Across I/O Mapping")
        axs[1, 0].set_xlabel("V_IN (V)")
        axs[1, 0].set_ylabel("V_OUT (V)")
        axs[1, 0].set_zlabel("V_MAX (V)")

        axs[0, 1].scatter(x_v_in, y_v_out, np.multiply(co_min, 1e6), c=co_min)
        axs[0, 1].set_title("Min. C_O Across I/O Mapping")
        axs[0, 1].set_xlabel("V_IN (V)")
        axs[0, 1].set_ylabel("V_OUT (V)")
        axs[0, 1].set_zlabel("Capacitance (uF)")

        axs[1, 1].scatter(x_v_in, y_v_out, v_co_max, c=v_co_max)
        axs[1, 1].set_title("Max. V_CO Across I/O Mapping")
        axs[1, 1].set_xlabel("V_IN (V)")
        axs[1, 1].set_ylabel("V_OUT (V)")
        axs[1, 1].set_zlabel("V_MAX (V)")

        axs[0, 2].scatter(x_v_in, y_v_out, np.multiply(l_min, 1e6), c=l_min)
        axs[0, 2].set_title("Min. L Across I/O Mapping")
        axs[0, 2].set_xlabel("V_IN (V)")
        axs[0, 2].set_ylabel("V_OUT (V)")
        axs[0, 2].set_zlabel("Inductance (uH)")

        axs[1, 2].scatter(x_v_in, y_v_out, i_l_max, c=i_l_max)
        axs[1, 2].set_title("Max. I_L Across I/O Mapping")
        axs[1, 2].set_xlabel("V_IN (V)")
        axs[1, 2].set_ylabel("V_OUT (V)")
        axs[1, 2].set_zlabel("Current (A)")

        plt.tight_layout()
        plt.savefig("capacitor_inductor_sizing_map.png")
        plt.show()

    # Encapsulate so I can fold
    plot()

    ci_min = np.max(ci_min)
    co_min = np.max(co_min)
    l_min = np.max(l_min)

    ci_vdc_min = np.max(v_ci_max) * sf
    co_vdc_min = np.max(v_co_max) * sf
    l_a_min = np.max(i_l_max) * 1.05  # override * sf

    return (ci_min, co_min, l_min, ci_vdc_min, co_vdc_min, l_a_min)


def get_inductor_sizing(l, i_max, b_sat, r_l):
    """_summary_
    Size the inductor.

    Args:
        l (float): Inductance, in H
        i_max (float): Max current, in A
        b_sat (float): Magnetic field saturation, in T
        r_l (float): Inductor current ripple ratio

    Returns:
        (float, ...): Set of floats consisting of:
            Maximum k_g
            Real k_g
            Magnetic field at AC, in T
            Number of turns
            Cross-sectional area of wire, in m^2
            Length of wire, in m^2
            Resistance of wire in Ohms
            Power loss from conduction, in W
    """

    # Assume PQ 26/25, B65877A
    k_g_target = 0.125  # cm^5
    A_c = 0.0001088  # cross sectional area of core, m^2
    A_n = 4.7e-5  # cross sectional area of winding, m^2
    l_n = 0.056  # length of turn, m
    rho = 2 * 1e-8
    k_u = 0.3  # Hand wound packing factor

    # choose b_sat from datasheet
    b_pk = b_sat * 0.75

    # Get number of turns
    N = m.ceil(l * i_max / (b_pk * A_c))

    # Get area of wire
    A_w = A_n * k_u / N

    # Get length of wire
    l_w = l_n * N

    # Get resistance of wire
    r_real = rho * l_w / A_w

    # Get power loss from conduction
    i_rms = i_max / m.sqrt(2)
    p_cond = i_rms**2 * r_real

    # Derive required k_g
    k_g = l**2 * i_max**2 * rho / (b_pk**2 * r_real * k_u) * 1e10

    # Get b_ac for core loss
    b_ac = b_pk * r_l / (1 + r_l)

    return (k_g_target, k_g, b_ac, N, A_w, l_w, r_real, p_cond)


def get_inductor_core_loss(p_v):
    """_summary_
    Get inductor core loss as a function of p_v and volume.

    Args:
def get_passive_sizing(operating_points, f_sw, r_ci_v, r_co_v, r_l_a, eff, sf=0.25):
    """_summary_
    Generat map of passive requirements for operation at various operating points.

    Args:
        v_in_range ([float]]): Input voltage range in format [min, best, max]
        v_out_range ([float]): Output voltage range in format [min, avg, max]
        f_sw (float): Switching frequency
        r_ci_v (float): Maximum allowed input capacitor voltage ripple
        r_co_v (float): Maximum allowed output capacitor voltage ripple
        r_l_a (float): Maximum allowed inductor current ripple
        eff (float): System efficiency
        model (func): Solar cell model
        num_cells (int): Number of solar cells
        sf (float, optional): Safety factor. Defaults to 0.25.

    Returns:
        (float, ...): Set of floats consisting of:
            Minimum input capacitance
            Minimum output capacitance
            Minimum inductance
            Minimum VDC for input capacitor
            Minimum VDC for output capacitor
            Minimum I_D for inductor
    """

    # Given that the PV is a nonlinear current source, it's not directly
    # straightforward to determine when ci, co, l are minimized. We do know,
    # however, that the minimum feasible passive value is bounded by the worst
    # input/output combo.
    ci_min = []
    co_min = []
    l_min = []
    i_l_max = []
    v_ci_max = []
    v_co_max = []

    x_v_in = []
    y_v_out = []

    for (v_in, i_in, v_out, i_out) in operating_points:
        p_in = v_in * i_in
        x_v_in.append(v_in)
        y_v_out.append(v_out)

        # ci = (r_l * i_in) / (8 * r_ci * v_out * f_sw)
        # co = (v_out - v_in) * p_in / (2 * r_co * v_out**3 * f_sw)

        i_out = p_in / v_out

        duty = 1 - v_in * eff / v_out
        l = v_in * (v_out - v_in) / (r_l_a * f_sw * v_out)
        r_l_a_op = v_in * duty / (f_sw * l)

        ci = r_l_a_op / (8 * f_sw * r_ci_v)

        co = (p_in / v_out * duty) / (f_sw * r_co_v)
        r_co_v_op = (v_out - v_in) * i_out / (v_out * f_sw * co)

        # print(f"\nI/O: {v_in :.3f}[{i_in :.3f}]/{v_out :.3f}[{i_out :.3f}]")
        # print(f"Duty: {duty :.3f}")
        # print(f"Min inductance: {l * 1E6 :.3f} uH")
        # print(f"Inductor ripple current: {r_l_a_op :.3f} A")

        # print(f"Min inp. cap.: {ci * 1E6 :.3f} uF")
        # print(f"Inp. cap. ripple voltage: {r_ci_v :.3f} V")

        # print(f"Min out. cap.: {co * 1E6 :.3f} uF")
        # print(f"Out. cap. ripple voltage: {r_co_v_op :.3f} V")

        ci_min.append(ci)
        co_min.append(co)
        l_min.append(l)
        i_l_max.append(r_l_a_op)
        v_ci_max.append(r_ci_v)
        v_co_max.append(r_co_v_op)

    def plot():
        # Plot out switching frequency map.
        fig, axs = plt.subplots(2, 3, subplot_kw=dict(projection="3d"))
        axs[0, 0].scatter(x_v_in, y_v_out, np.multiply(ci_min, 1e6), c=ci_min)
        axs[0, 0].set_title("Min. C_I Across I/O Mapping")
        axs[0, 0].set_xlabel("V_IN (V)")
        axs[0, 0].set_ylabel("V_OUT (V)")
        axs[0, 0].set_zlabel("Capacitance (uF)")

        axs[1, 0].scatter(x_v_in, y_v_out, v_ci_max, c=v_ci_max)
        axs[1, 0].set_title("Max. V_CI Across I/O Mapping")
        axs[1, 0].set_xlabel("V_IN (V)")
        axs[1, 0].set_ylabel("V_OUT (V)")
        axs[1, 0].set_zlabel("V_MAX (V)")

        axs[0, 1].scatter(x_v_in, y_v_out, np.multiply(co_min, 1e6), c=co_min)
        axs[0, 1].set_title("Min. C_O Across I/O Mapping")
        axs[0, 1].set_xlabel("V_IN (V)")
        axs[0, 1].set_ylabel("V_OUT (V)")
        axs[0, 1].set_zlabel("Capacitance (uF)")

        axs[1, 1].scatter(x_v_in, y_v_out, v_co_max, c=v_co_max)
        axs[1, 1].set_title("Max. V_CO Across I/O Mapping")
        axs[1, 1].set_xlabel("V_IN (V)")
        axs[1, 1].set_ylabel("V_OUT (V)")
        axs[1, 1].set_zlabel("V_MAX (V)")

        axs[0, 2].scatter(x_v_in, y_v_out, np.multiply(l_min, 1e6), c=l_min)
        axs[0, 2].set_title("Min. L Across I/O Mapping")
        axs[0, 2].set_xlabel("V_IN (V)")
        axs[0, 2].set_ylabel("V_OUT (V)")
        axs[0, 2].set_zlabel("Inductance (uH)")

        axs[1, 2].scatter(x_v_in, y_v_out, i_l_max, c=i_l_max)
        axs[1, 2].set_title("Max. I_L Across I/O Mapping")
        axs[1, 2].set_xlabel("V_IN (V)")
        axs[1, 2].set_ylabel("V_OUT (V)")
        axs[1, 2].set_zlabel("Current (A)")

        plt.tight_layout()
        plt.savefig("capacitor_inductor_sizing_map.png")
        plt.show()

    # Encapsulate so I can fold
    plot()

    ci_min = np.max(ci_min)
    co_min = np.max(co_min)
    l_min = np.max(l_min)

    ci_vdc_min = np.max(v_ci_max) * sf
    co_vdc_min = np.max(v_co_max) * sf
    l_a_min = np.max(i_l_max) * 1.05  # override * sf

    return (ci_min, co_min, l_min, ci_vdc_min, co_vdc_min, l_a_min)


def get_inductor_sizing(l, i_max, b_sat, r_l):
    """_summary_
    Size the inductor.

    Args:
        l (float): Inductance, in H
        i_max (float): Max current, in A
        b_sat (float): Magnetic field saturation, in T
        r_l (float): Inductor current ripple ratio

    Returns:
        (float, ...): Set of floats consisting of:
            Maximum k_g
            Real k_g
            Magnetic field at AC, in T
            Number of turns
            Cross-sectional area of wire, in m^2
            Length of wire, in m^2
            Resistance of wire in Ohms
            Power loss from conduction, in W
    """

    # Assume PQ 26/25, B65877A
    k_g_target = 0.125  # cm^5
    A_c = 0.0001088  # cross sectional area of core, m^2
    A_n = 4.7e-5  # cross sectional area of winding, m^2
    l_n = 0.056  # length of turn, m
    rho = 2 * 1e-8
    k_u = 0.3  # Hand wound packing factor

    # choose b_sat from datasheet
    b_pk = b_sat * 0.75

    # Get number of turns
    N = m.ceil(l * i_max / (b_pk * A_c))

    # Get area of wire
    A_w = A_n * k_u / N

    # Get length of wire
    l_w = l_n * N

    # Get resistance of wire
    r_real = rho * l_w / A_w

    # Get power loss from conduction
    i_rms = i_max / m.sqrt(2)
    p_cond = i_rms**2 * r_real

    # Derive required k_g
    k_g = l**2 * i_max**2 * rho / (b_pk**2 * r_real * k_u) * 1e10

    # Get b_ac for core loss
    b_ac = b_pk * r_l / (1 + r_l)

    return (k_g_target, k_g, b_ac, N, A_w, l_w, r_real, p_cond)


def get_inductor_core_loss(p_v):
    """_summary_
    Get inductor core loss as a function of p_v and volume.

    Args:
        p_v (float): loss, in kW/m^3 as chosen on chart

    Returns:
        float: loss, in W
    """
    vol = 6.54e-6  # m^3
    return p_v * vol * 1e3


def get_capacitor_esr(c, f_sw, df):
    ESR = df / (2 * m.pi * f_sw * c)
    return ESR


def get_capacitor_impedance(c, f_sw):
    return 1 / (2 * m.pi * f_sw * c)


def get_capacitor_v_rms(v_pp):
    return v_pp / (2 * m.sqrt(2))


def get_capacitor_i_rms(v_rms, z):
    return v_rms / z




def get_two_caps_parallel(f_sw, z1, z2):
    c1, r1 = z1
    c2, r2 = z2

    num = (r1 + 1 / (1j * f_sw * c1)) * (r2 + 1 / (1j * f_sw * c2))
    denom = (r1 + 1 / (1j * f_sw * c1)) + (r2 + 1 / (1j * f_sw * c2))
    print(z1, z2)
    print(num, denom)
    return (num / denom).imag, (num / denom).real

        p_v (float): loss, in kW/m^3 as chosen on chart

    Returns:
        float: loss, in W
    """
    vol = 6.54e-6  # m^3
    return p_v * vol * 1e3


def get_capacitor_esr(c, f_sw, df):
    ESR = df / (2 * m.pi * f_sw * c)
    return ESR


def get_capacitor_impedance(c, f_sw):
    return 1 / (2 * m.pi * f_sw * c)


def get_capacitor_v_rms(v_pp):
    return v_pp / (2 * m.sqrt(2))


def get_capacitor_i_rms(v_rms, z):
    return v_rms / z




def get_two_caps_parallel(f_sw, z1, z2):
    c1, r1 = z1
    c2, r2 = z2

    num = (r1 + 1 / (1j * f_sw * c1)) * (r2 + 1 / (1j * f_sw * c2))
    denom = (r1 + 1 / (1j * f_sw * c1)) + (r2 + 1 / (1j * f_sw * c2))
    print(z1, z2)
    print(num, denom)
    return (num / denom).imag, (num / denom).real




