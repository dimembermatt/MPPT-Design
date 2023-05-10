    # Determine top 12.5 percentile FOM
    switches_filt = switches_filt.copy()
    switches_filt["fom (ps)"] = (
        switches_filt["R_DS_ON (mO)"] * switches_filt["C_OSS (pF)"] / 1000
    )
    fom = switches_filt["fom (ps)"].quantile(0.125) * 1e-12
    logging.info(f"Target switch FOM: {fom} s")

    # Determine optimal R_DS_ON
    duty = map["duty"]
    op = [
        ["MIN_SW_STRESS", duty[0][0], duty[0][1], duty[0][2]],
        ["MAX_SW_STRESS", duty[1][0], duty[1][1], duty[1][2]],
    ]
    worst_op, worst_f_sw, worst_r_ds_on = get_rdson_vs_fsw_map(
        fom, op, p_sw_bud, ind["r_l"]
    )
    if worst_op is None:
        # TODO: attempt with lower inductor current, larger switch power allocation
        raise Exception(
            "The switch losses are too large for the MAX_SW_STRESS operating point."
            "Modify the input/output user voltage range ('user_v_range') to reduce the switch stress."
        )

    logging.info(f"Target switch R_DS_ON: {worst_r_ds_on} O")
    logging.info(f"Target switch F_SW: {worst_f_sw} hz")

    # Choose switch closest to target R_DS_ON and with lowest FOM
    def switch_fom(point, target):
        return m.dist([point[0]], [target[0]]) * point[1]

    switches_filt["sw_fom"] = switches_filt.apply(
        lambda row: switch_fom(
            (row["R_DS_ON (mO)"], row["fom (ps)"]), (worst_r_ds_on * 1e3, fom * 1e12)
        ),
        axis=1,
    )
    optimal_sw = switches_filt.nsmallest(1, "sw_fom")
    logging.info(f"Switches: {switches_filt}")
    logging.info(f"Optimal switch: {optimal_sw}")

    (f_sw_min, vi_min, ii_min, vo_min) = get_switch_op_fs_map(
        map["points"],
        list(optimal_sw["R_DS_ON (mO)"])[0] * 1e-3,
        list(optimal_sw["C_OSS (pF)"])[0] * 1e-12,
        p_sw_bud,
        ind["r_l"],
    )
    logging.info(f"Actual F_SW: {f_sw_min} hz")