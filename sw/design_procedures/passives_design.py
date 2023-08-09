"""_summary_
@file       passives_design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate design parameters of passives (capacitors, inductors) for
            a DC-DC boost converter. 
@sources    - TI AN SLVA372D
            - TI AR SLVAF30
@version    1.0.0
@date       2023-05-06
@file_overview
    optimize_passives
        get_passive_requirements
            get_cap_and_ind
            get_ripple

            (ci_min, ci_v, ci_vpp),
            (co_min, co_v, co_vpp),
            (l_min, l_i, l_ipp)

        get_inp_cap / get_out_cap
            get_bulk_cap
                filter electrolytics based on requirements
                minimize_pdis
                    get_cap_losses
                        get_ripple_loss
                        get_leakage_loss

                set of best bulk cap candidates

            get_hf_cap
                filter electrolytics based on requirements
                minimize_pdis
                    get_cap_losses
                        get_ripple_loss
                        get_leakage_loss

                set of best hf cap candidates

            set of best bulk and hf cap candidates

        get_inductor
            get_core_size

            get_core_material

            get_num_turns
            get_wire_cross_area
            get_gap_size

            get_ind_losses
                get_core_losses
                get_cond_losses

        get_worst_case_losses
            inductor losses
            inp cap losses
            out cap losses

        returns chosen caps, ind, worst case loss for inp caps, out caps, ind

    map_passives
        map_inp_vripple
        map_out_vripple
        map_ind_iripple
        map_inp_cap_losses
        map_out_cap_losses
        map_ind_losses
        map_ind_thermals
"""

import logging
import math as m

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

k_u = 0.7  # Winding factor
rho = 2.08 * 1e-8


def get_capacitance_and_inductance(vi, ii, vo, io, f_sw, r_l, r_ci_v, r_co_v):
    pi = vi * ii
    io = pi / vo
    d = 1 - vi / vo

    # These three are dependent on ripple ratio
    # r_l = r_l_a / (2 * ii)
    # r_ci = r_ci_v / (2 * vi)
    # r_co = r_co_v / (2 * vo)

    # l = vi**2 * (vo - vi) / (2 * f_sw * r_l * pi * vo)
    # ci = r_l * pi / (8 * f_sw * r_ci * vi**2)
    # co = pi * (vo - vi) / (2 * f_sw * r_co * vo**3)

    # These three are dependent on absolute ripple/
    # ci = ii * d * (1 - d) / (r_ci_v * f_sw)
    # co = io * d / (r_co_v * f_sw)
    # l = vi * d / (r_l_a * f_sw)

    # ci = r_l_a / (8 * vi * f_sw)
    # co = io * d / (f_sw * r_co_v)
    # l = vi * (vo - vi) / (f_sw * vo * r_l_a)

    r_l_a = r_l * 2 * ii
    ci = r_l_a / (8 * f_sw * r_ci_v)
    co = d * pi / (f_sw * vo * r_co_v)
    l = d * vi / (f_sw * r_l_a)

    return ci, co, l


def get_ripple(vi, ii, vo, ci, co, l, f_sw):
    pi = vi * ii
    d = 1 - vi / vo

    r_l_a = d * vi / (f_sw * l)
    r_ci_v = r_l_a / (8 * f_sw * ci)
    r_co_v = d * pi / (f_sw * vo * co)

    return r_ci_v, r_co_v, r_l_a


def get_requirements(points, f_sw, r_ci_v, r_co_v, r_l, sf=1.00):
    # Get the capacitance and inductance required to hit the ripple
    # specification across all op
    def _get_capacitance_and_inductance(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        io = point["IO (A)"]
        return pd.Series(
            get_capacitance_and_inductance(vi, ii, vo, io, f_sw, r_l, r_ci_v, r_co_v)
        )

    points[["CI (F)", "CO (F)", "L (H)"]] = points.apply(
        _get_capacitance_and_inductance, axis=1
    )

    # Identify the worst case capacitance and inductance required
    ci = np.max(points["CI (F)"])
    co = np.max(points["CO (F)"])
    l = np.max(points["L (H)"])

    # Using the worst case capacitance and inductance, determine the actual
    # ripple across all op
    def _get_ripple(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        vi_pp, vo_pp, ii_pp = get_ripple(vi, ii, vo, ci, co, l, f_sw)
        return pd.Series(
            [vi + vi_pp / 2, vi_pp, vo + vo_pp / 2, vo_pp, ii + ii_pp / 2, ii_pp]
        )

    points[
        ["VIm (V)", "VIpp (V)", "VOm (V)", "VOpp (V)", "IIm (A)", "IIpp (A)"]
    ] = points.apply(_get_ripple, axis=1)

    return (
        (
            np.max(points["CI (F)"]),
            np.max(points["VIm (V)"]),
            np.max(points["VIpp (V)"]),
        ),
        (
            np.max(points["CO (F)"]),
            np.max(points["VOm (V)"]),
            np.max(points["VOpp (V)"]),
        ),
        (
            np.max(points["L (H)"]),
            np.max(points["IIm (A)"]),
            np.max(points["IIpp (A)"]),
        ),
    )


def get_capacitor_leakage_loss(i_leakage, v_peak):
    return i_leakage * v_peak


def get_capacitor_ripple_loss(esr, i_rms):
    return i_rms**2 * esr


def get_capacitor_losses(capacitors, i_pp, v_p):
    p_ripple = 0.0
    p_leakage = 0.0
    i_rms = get_i_rms(i_pp)

    # Bulk capacitor losses
    for _, capacitor in capacitors[0].iterrows():
        p_leakage += get_capacitor_leakage_loss(capacitor["LEAKAGE (uA)"] * 1e-6, v_p)
        p_ripple += get_capacitor_ripple_loss(capacitor["ESR (mO)"] * 1e-3, i_rms)

    # TODO: hf capacitor losses
    # for _, capacitor in capacitors[1].iterrows():
    #     p_leakage += 0
    #     p_ripple += 0

    p_tot = p_ripple + p_leakage

    return p_ripple, p_leakage, p_tot


def get_i_rms(i_pp):
    return i_pp / (2 * m.sqrt(2))


def get_capacitor_fom(electrolytic):
    v_d = electrolytic["V_D (V)"]
    capacitance = electrolytic["Capacitance (uF)"]
    esr = electrolytic["ESR (mO)"]
    ripple = electrolytic["I_RIPPLE 125 C (mA)"]
    if m.isnan(ripple):
        ripple = electrolytic["I_RIPPLE 105 C (mA)"]
    leakage = electrolytic["LEAKAGE (uA)"]
    cost = electrolytic["Cost ($)"]
    return (v_d * capacitance * ripple) / (esr * leakage * cost)


def get_optimal_bulk_capacitors(electrolytics, c_min, v_max, _, i_pkpk):
    # Maximum expected I_RMS that must be distributed among all caps
    i_rms = get_i_rms(i_pkpk)

    # Filter caps.
    electrolytics = electrolytics[(electrolytics["V_D (V)"] > v_max)]
    electrolytics = electrolytics.copy()
    electrolytics["FOM"] = electrolytics.apply(get_capacitor_fom, axis=1)
    # print(electrolytics)

    bulk_caps = pd.DataFrame()
    c_remainder = c_min * 1e6  # uF
    i_remainder = i_rms * 1e3  # mA

    while c_remainder > 0 or i_remainder > 0:
        # Pick best capacitor that closest meets the spec
        candidate = electrolytics.nlargest(1, "FOM")

        c = candidate.iloc[0]["Capacitance (uF)"]
        i = candidate.iloc[0]["I_RIPPLE 125 C (mA)"]
        if m.isnan(i):
            i = candidate.iloc[0]["I_RIPPLE 105 C (mA)"]
        c_remainder -= c
        i_remainder -= i
        bulk_caps = pd.concat([bulk_caps, candidate], ignore_index=True)

    return bulk_caps


def get_optimal_hf_capacitors(mlccs, cap_reqs):
    TODO: this
    pass


def size_inductor(inductor_shape, inductor_material, f_sw, l, i_p, i_pp):
    # Get shape properties
    k_g_target = inductor_shape.iloc[0]["K_G (mm^5)"] * 1e-15
    volume_core = inductor_shape.iloc[0]["VOLUME (mm^3)"] * 1e-9
    area_core = inductor_shape.iloc[0]["CORE_CSA (mm^2)"] * 1e-6
    area_winding = inductor_shape.iloc[0]["WINDING_CSA (mm^2)"] * 1e-6
    length_turn = inductor_shape.iloc[0]["TURN_LENGTH (mm)"] * 1e-3

    # Get material properties
    # Select the material that meets frequency
    material = inductor_material.loc[
        (inductor_material["FREQ_MIN (Hz)"] <= f_sw)
        & (inductor_material["FREQ_MAX (Hz)"] >= f_sw)
    ]
    if material.empty:
        raise Exception(
            f"The material {inductor_material.iloc[0]['MATERIAL']} has no matching frequency regime for {f_sw}!"
        )
    cm = material.iloc[0]["Cm"]
    x = material.iloc[0]["X"]
    y = material.iloc[0]["Y"]
    ct2 = material.iloc[0]["Ct2"]
    ct1 = material.iloc[0]["Ct1"]
    ct0 = material.iloc[0]["Ct0"]

    b_sat = inductor_material.iloc[0]["B_SAT (mT)"] * 1e-3

    # Get max b_saturation from core material
    b_pk = b_sat * 0.75

    # Get number of turns
    N = m.ceil(l * i_p / (b_pk * area_core))
    l = N * b_pk * area_core / i_p

    # Get gap length
    permittivity_free_space = 4 * m.pi * 1e-7  # H/m
    permittivity_PTFE_shim = 2.1 * permittivity_free_space
    length_gap = N**2 * area_core * permittivity_PTFE_shim / l

    # Get length of wire
    length_wire = length_turn * N

    # Expected area available
    area_available = area_winding * k_u

    # Get area of wire by consuming all available area
    area_wire = area_available / N

    # Get resistance of wire
    w_resistance = rho * length_wire / area_wire

    # Get conduction loss
    i_rms = get_i_rms(i_p)
    p_cond = i_rms**2 * w_resistance

    # Derive k_g (m^5)
    k_g = l**2 * i_p**2 * rho / (b_pk**2 * w_resistance * k_u)

    # Get b_ac for core loss
    r_l = i_pp / i_p / 2
    b_ac = b_pk * r_l / (1 + r_l)
    t_max = 100  # C
    p_v = cm * f_sw**x * b_ac**y * (ct2 * t_max**2 - ct1 * t_max + ct0)  # W/m^3
    p_core = p_v * volume_core

    # print(f"KG: {k_g_target * 1e10 :.3f} >= {k_g * 1e10 :.3f} cm^5")
    # print(f"b_sat: {b_sat :.3f} T, b_pk: {b_pk :.3f} T")
    # print(f"Num turns: {N}")
    # print(f"gap length: {length_gap * 1e3 :.3f} mm")
    # print(f"Wire length: {length_wire :.3f} m")
    # print(f"Available winding CSA: {area_available * 1e6 :.3f} mm^2")
    # print(f"Target wire CSA: {area_wire * 1e6 :.3f} mm^2")
    # print(f"Wire resistance and loss: {w_resistance :.3f} ohm, {p_cond :.3f} W")
    # print(f"Core loss: {b_ac * 1e3 :.3f} mT, {p_core :.5f} W")

    return l, N, length_wire, area_wire, length_gap, p_cond, p_core


def get_wire_gauge(awg, area_wire):
    # Must be <= the area otherwise it won't fit
    awg_filt = awg[awg["CROSS_SECTION (mm^2)"] <= area_wire]
    awg_fit = awg_filt.nlargest(1, "CROSS_SECTION (mm^2)")
    return awg_fit.iloc[0]["AWG"]


def get_inductor_losses(inductor, shape, material, f_sw, i_p, i_pp):
    volume_core = shape.iloc[0]["VOLUME (mm^3)"] * 1e-9
    cm = material.iloc[0]["Cm"]
    x = material.iloc[0]["X"]
    y = material.iloc[0]["Y"]
    ct2 = material.iloc[0]["Ct2"]
    ct1 = material.iloc[0]["Ct1"]
    ct0 = material.iloc[0]["Ct0"]
    b_sat = material.iloc[0]["B_SAT (mT)"] * 1e-3

    # Get conduction loss
    length_wire = inductor.iloc[0]["WIRE_LENGTH (m)"]
    area_wire = inductor.iloc[0]["WIRE_AREA (m^2)"]
    i_rms = get_i_rms(i_p)
    w_resistance = rho * length_wire / area_wire
    p_cond = i_rms**2 * w_resistance

    # Get core loss
    r_l = i_pp / i_p / 2
    b_pk = b_sat * 0.75
    b_ac = b_pk * r_l / (1 + r_l)
    t_max = 100  # C
    p_v = cm * f_sw**x * b_ac**y * (ct2 * t_max**2 - ct1 * t_max + ct0)  # W/m^3
    p_core = p_v * volume_core

    p_tot = p_cond + p_core
    return p_cond, p_core, p_tot


def optimize_passives(
    design, capacitors, inductors, inductor_shapes, inductor_materials, awg
):
    sw = design["switches"]
    ci = design["input_cap"]
    co = design["output_cap"]
    l = design["inductor"]
    map = design["map"]
    sf = design["safety_factor"]

    # Get passive requirements
    (ci_reqs, co_reqs, l_reqs) = get_requirements(
        map["points"],
        sw["f_sw"],
        ci["v_pp"],
        co["v_pp"],
        l["r_l"],
        sf=sf,
    )

    logging.info(
        f"Input capacitor requirements:"
        f"\n\tC >= {ci_reqs[0] * 1e6 :.3f} uF"
        f"\n\tV >= {ci_reqs[1] :.3f} V"
        f"\n\tIrms >= {get_i_rms(l_reqs[2]) * 1e3} mA"
    )

    logging.info(
        f"Output capacitor requirements:"
        f"\n\tC >= {co_reqs[0] * 1e6 :.3f} uF"
        f"\n\tV >= {co_reqs[1] :.3f} V"
        f"\n\tIrms >= {get_i_rms(l_reqs[2]) * 1e3} mA"
    )

    logging.info(
        f"Inductor requirements:"
        f"\n\tL >= {l_reqs[0] * 1e6 :.3f} uH"
        f"\n\tI >= {l_reqs[1]} A"
    )

    # Get optimal input and output cap sets
    def get_optimal_capacitors(capacitors, cap_reqs, i_pp):
        # Get optimal bulk capacitors
        bulk_caps = get_optimal_bulk_capacitors(
            capacitors[(capacitors["Capacitor Type"] == "Electrolytic")],
            *cap_reqs,
            i_pp,
        )

        # Get optimal hf capacitors
        hf_caps = get_optimal_hf_capacitors(
            capacitors[(capacitors["Capacitor Type"] == "MLCC")], cap_reqs
        )

        return (bulk_caps, hf_caps)

    optimal_inp_caps = get_optimal_capacitors(
        capacitors,
        ci_reqs,
        l_reqs[2],
    )
    optimal_out_caps = get_optimal_capacitors(
        capacitors,
        co_reqs,
        l_reqs[2],
    )

    # Get optimal inductor
    def get_optimal_inductor(inductors, f_sw, ind_reqs):
        # Size each inductor listed
        def optimize_inductor(inductor):
            inductor_shape = inductor_shapes[
                (inductor_shapes["SHAPE"] == inductor["SHAPE"])
            ]
            inductor_material = inductor_materials[
                (inductor_materials["MATERIAL"] == inductor["MATERIAL"])
            ]

            try:
                (
                    _l,
                    N,
                    length_wire,
                    area_wire,
                    length_gap,
                    p_cond,
                    p_core,
                ) = size_inductor(inductor_shape, inductor_material, f_sw, *ind_reqs)
                return pd.Series(
                    [
                        _l * 1e6,
                        N,
                        length_wire,
                        area_wire,
                        length_gap * 1e6,
                        p_cond,
                        p_core,
                        p_core + p_cond,
                    ]
                )
            except Exception as e:
                # print(e)
                return pd.Series([pd.NaT] * 8)

        inductors[
            [
                "INDUCTANCE (uH)",
                "NUM_TURNS",
                "WIRE_LENGTH (m)",
                "WIRE_AREA (m^2)",
                "GAP_LENGTH (um)",
                "CONDUCTION_LOSS (W)",
                "CORE_LOSS (W)",
                "TOTAL_LOSS (W)",
            ]
        ] = inductors.apply(optimize_inductor, axis=1)
        inductors = inductors.dropna()

        # Get inductor that consumes the least power
        try:
            optimal_inductor = inductors.nsmallest(1, "TOTAL_LOSS (W)")
        except Exception as e:
            # print(e)
            # Exception for material with no support for frequency
            inductors = inductors.copy()
            inductors["TOTAL_LOSS (W)"] = inductors["TOTAL_LOSS (W)"].astype(float)
            optimal_inductor = inductors.nsmallest(1, "TOTAL_LOSS (W)")
        return optimal_inductor

    optimal_inductor = get_optimal_inductor(inductors, sw["f_sw"], l_reqs)
    try:
        optimal_inductor_shape = inductor_shapes[
            (inductor_shapes["SHAPE"] == optimal_inductor.iloc[0]["SHAPE"])
        ]
        optimal_inductor_material = inductor_materials[
            (inductor_materials["MATERIAL"] == optimal_inductor.iloc[0]["MATERIAL"])
        ]
    except Exception as e:
        # print(e)
        raise Exception("No inductor possible")

    # Get worst case losses
    p_ci_ripple, p_ci_leakage, p_ci_loss = get_capacitor_losses(
        optimal_inp_caps, l_reqs[2], ci_reqs[1]
    )
    p_co_ripple, p_co_leakage, p_co_loss = get_capacitor_losses(
        optimal_out_caps, l_reqs[2], co_reqs[1]
    )

    p_l_cond, p_l_core, p_l_loss = get_inductor_losses(
        optimal_inductor,
        optimal_inductor_shape,
        optimal_inductor_material,
        sw["f_sw"],
        l_reqs[1],
        l_reqs[2],
    )
    # TODO: losses slightly different for some reason
    # print(p_l_cond, p_l_core, p_l_loss)
    # p_l_cond = optimal_inductor.iloc[0]["CONDUCTION_LOSS (W)"]
    # p_l_core = optimal_inductor.iloc[0]["CORE_LOSS (W)"]
    # p_l_loss = optimal_inductor.iloc[0]["TOTAL_LOSS (W)"]
    # print(p_l_cond, p_l_core, p_l_loss)

    logging.info(
        f"Input capacitors selected:"
        f"\n\tBulk caps: {optimal_inp_caps[0].iloc[:]['PART_NAME'].to_string(index=False)}"
        # f"\n\tHF caps: {optimal_inp_caps[1].iloc[:]['PART_NAME'].to_string(index=False)}"
    )

    logging.info(
        f"Output capacitors selected:"
        f"\n\tBulk caps: {optimal_out_caps[0].iloc[:]['PART_NAME'].to_string(index=False)}"
        # f"\n\tHF caps: {optimal_out_caps[1].iloc[:]['PART_NAME'].to_string(index=False)}"
    )

    logging.info(
        f"Input inductor selected:"
        f"\n\t{optimal_inductor.iloc[0]['PART_NAME']}"
        f"\n\twith {optimal_inductor.iloc[0]['NUM_TURNS']} turns "
        f"of {int(get_wire_gauge(awg, optimal_inductor.iloc[0]['WIRE_AREA (m^2)'] * 1e6))} gauge wire"
        f"\n\tand a core gap of {optimal_inductor.iloc[0]['GAP_LENGTH (um)'] / 2 / 1e3 :.1f} mm "
        f"per side of the core."
    )

    return (
        (optimal_inp_caps, p_ci_loss),
        (optimal_out_caps, p_co_loss),
        (optimal_inductor, p_l_loss),
    )


def map_ripple(inp_caps, out_caps, ind, points, f_sw, output_path):
    ci = (
        inp_caps[0]["Capacitance (uF)"].sum() * 1e-6
    )  # + inp_caps[1]["Capacitance (uF)"].sum()
    co = (
        out_caps[0]["Capacitance (uF)"].sum() * 1e-6
    )  # + out_caps[1]["Capacitance (uF)"].sum()
    l = ind.iloc[0]["INDUCTANCE (uH)"] * 1e-6

    def _get_ripple(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        return pd.Series(get_ripple(vi, ii, vo, ci, co, l, f_sw))

    points[["VIpp (V)", "VOpp (V)", "IIpp (A)"]] = points.apply(_get_ripple, axis=1)

    # Plot out ripple map.
    fig, axs = plt.subplots(1, 3, subplot_kw={"projection": "3d"})
    fig.suptitle("Ripple Across I/O Map")
    axs[0].scatter(
        points["VI (V)"], points["VO (V)"], points["VIpp (V)"], c=points["VIpp (V)"]
    )
    axs[0].set_title("Input Voltage Ripple")
    axs[0].set_xlabel("$V_{IN}$ (V)")
    axs[0].set_ylabel("$V_{OUT}$ (V)")
    axs[0].set_zlabel("$VI_{PP}$ (V)")

    axs[1].scatter(
        points["VI (V)"], points["VO (V)"], points["VOpp (V)"], c=points["VOpp (V)"]
    )
    axs[1].set_title("Output Voltage Ripple")
    axs[1].set_xlabel("$V_{IN}$ (V)")
    axs[1].set_ylabel("$V_{OUT}$ (V)")
    axs[1].set_zlabel("$VO_{PP}$ (V)")

    axs[2].scatter(
        points["VI (V)"], points["VO (V)"], points["IIpp (A)"], c=points["IIpp (A)"]
    )
    axs[2].set_title("Inductor Current Ripple")
    axs[2].set_xlabel("$V_{IN}$ (V)")
    axs[2].set_ylabel("$V_{OUT}$ (V)")
    axs[2].set_zlabel("$II_{PP}$ (A)")

    fig.set_size_inches(12, 5)
    plt.tight_layout()
    plt.subplots_adjust(right=0.94, wspace=0.15)
    plt.show()
    fig.savefig(output_path + "/08_passive_ripple_map.png")
    plt.close()

    logging.info(
        f"Worst case ripple:"
        f"\n\tInput voltage ripple: {np.max(points['VIpp (V)']) :.3f} V"
        f"\n\tOutput voltage ripple: {np.max(points['VOpp (V)']) :.3f} V"
        f"\n\tInductor current ripple: {np.max(points['IIpp (A)']) :.3f} A"
    )

    return points


def map_losses(
    inp_caps, out_caps, ind, ind_shape, ind_material, points, f_sw, output_path
):
    ci = (
        inp_caps[0]["Capacitance (uF)"].sum() * 1e-6
    )  # + inp_caps[1]["Capacitance (uF)"].sum()
    co = (
        out_caps[0]["Capacitance (uF)"].sum() * 1e-6
    )  # + out_caps[1]["Capacitance (uF)"].sum()
    l = ind.iloc[0]["INDUCTANCE (uH)"] * 1e-6

    def _get_ripple(point):
        vi = point["VI (V)"]
        vo = point["VO (V)"]
        ii = point["II (A)"]
        vi_pp, vo_pp, ii_pp = get_ripple(vi, ii, vo, ci, co, l, f_sw)
        return pd.Series(
            [vi + vi_pp / 2, vi_pp, vo + vo_pp / 2, vo_pp, ii + ii_pp / 2, ii_pp]
        )

    points[
        ["VIm (V)", "VIpp (V)", "VOm (V)", "VOpp (V)", "IIm (A)", "IIpp (A)"]
    ] = points.apply(_get_ripple, axis=1)

    def _get_losses(point):
        vi_p = point["VIm (V)"]
        ii_p = point["IIm (A)"]
        ii_pp = point["IIpp (A)"]
        vo_p = point["VOm (V)"]

        pi_ripple, pi_leakage, pi_tot = get_capacitor_losses(inp_caps, ii_pp, vi_p)
        po_ripple, po_leakage, po_tot = get_capacitor_losses(out_caps, ii_pp, vo_p)
        pl_cond, pl_core, pl_tot = get_inductor_losses(
            ind, ind_shape, ind_material, f_sw, ii_p, ii_pp
        )

        return pd.Series(
            [
                pi_ripple,
                pi_leakage,
                pi_tot,
                po_ripple,
                po_leakage,
                po_tot,
                pl_cond,
                pl_core,
                pl_tot,
            ]
        )

    points[
        [
            "PI_RIPPLE (W)",
            "PI_LEAK (W)",
            "PI_TOT (W)",
            "PO_RIPPLE (W)",
            "PO_LEAK (W)",
            "PO_TOT (W)",
            "PL_COND (W)",
            "PL_CORE (W)",
            "PL_TOT (W)",
        ]
    ] = points.apply(_get_losses, axis=1)

    fig, axs = plt.subplots(3, 3, subplot_kw={"projection": "3d"})
    fig.suptitle("Passives Losses Across I/O Map")

    axs[0][0].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PI_RIPPLE (W)"],
        c=points["PI_RIPPLE (W)"],
    )
    axs[0][0].set_title("Input Capacitor Ripple Loss")
    axs[0][0].set_xlabel("$V_{IN}$ (V)")
    axs[0][0].set_ylabel("$V_{OUT}$ (V)")
    axs[0][0].set_zlabel("$P_{RIPPLE}$ (W)")

    axs[1][0].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PI_LEAK (W)"],
        c=points["PI_LEAK (W)"],
    )
    axs[1][0].set_title("Input Capacitor Leakage Loss")
    axs[1][0].set_xlabel("$V_{IN}$ (V)")
    axs[1][0].set_ylabel("$V_{OUT}$ (V)")
    axs[1][0].set_zlabel("$P_{LEAK}$ (W)")

    axs[2][0].scatter(
        points["VI (V)"], points["VO (V)"], points["PI_TOT (W)"], c=points["PI_TOT (W)"]
    )
    axs[2][0].set_title("Input Capacitor Total Loss")
    axs[2][0].set_xlabel("$V_{IN}$ (V)")
    axs[2][0].set_ylabel("$V_{OUT}$ (V)")
    axs[2][0].set_zlabel("$P_{TOT}$ (W)")

    axs[0][1].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PO_RIPPLE (W)"],
        c=points["PO_RIPPLE (W)"],
    )
    axs[0][1].set_title("Output Capacitor Ripple Loss")
    axs[0][1].set_xlabel("$V_{IN}$ (V)")
    axs[0][1].set_ylabel("$V_{OUT}$ (V)")
    axs[0][1].set_zlabel("$P_{RIPPLE}$ (W)")

    axs[1][1].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PO_LEAK (W)"],
        c=points["PO_LEAK (W)"],
    )
    axs[1][1].set_title("Output Capacitor Leakage Loss")
    axs[1][1].set_xlabel("$V_{IN}$ (V)")
    axs[1][1].set_ylabel("$V_{OUT}$ (V)")
    axs[1][1].set_zlabel("$P_{LEAK}$ (W)")

    axs[2][1].scatter(
        points["VI (V)"], points["VO (V)"], points["PO_TOT (W)"], c=points["PO_TOT (W)"]
    )
    axs[2][1].set_title("Output Capacitor Total Loss")
    axs[2][1].set_xlabel("$V_{IN}$ (V)")
    axs[2][1].set_ylabel("$V_{OUT}$ (V)")
    axs[2][1].set_zlabel("$P_{TOT}$ (W)")

    axs[0][2].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PL_COND (W)"],
        c=points["PL_COND (W)"],
    )
    axs[0][2].set_title("Inductor Conduction Loss")
    axs[0][2].set_xlabel("$V_{IN}$ (V)")
    axs[0][2].set_ylabel("$V_{OUT}$ (V)")
    axs[0][2].set_zlabel("$P_{COND}$ (W)")

    axs[1][2].scatter(
        points["VI (V)"],
        points["VO (V)"],
        points["PL_CORE (W)"],
        c=points["PL_CORE (W)"],
    )
    axs[1][2].set_title("Inductor Core Loss")
    axs[1][2].set_xlabel("$V_{IN}$ (V)")
    axs[1][2].set_ylabel("$V_{OUT}$ (V)")
    axs[1][2].set_zlabel("$P_{CORE}$ (W)")

    axs[2][2].scatter(
        points["VI (V)"], points["VO (V)"], points["PL_TOT (W)"], c=points["PL_TOT (W)"]
    )
    axs[2][2].set_title("Inductor Total Loss")
    axs[2][2].set_xlabel("$V_{IN}$ (V)")
    axs[2][2].set_ylabel("$V_{OUT}$ (V)")
    axs[2][2].set_zlabel("$P_{TOT}$ (W)")

    fig.set_size_inches(12, 12)
    plt.tight_layout()
    plt.subplots_adjust(right=0.94, wspace=0.15)
    plt.show()
    fig.savefig(output_path + "/09_passive_losses_map.png")
    plt.close()

    logging.info(
        f"Worst case input capacitor ripple, leakage, and total loss:"
        f"\n\tRipple loss: {np.max(points['PI_RIPPLE (W)']) :.3f} W"
        f"\n\tLeakage loss: {np.max(points['PI_LEAK (W)']) :.3f} W"
        f"\n\tTotal loss: {np.max(points['PI_TOT (W)']) :.3f} W"
    )

    logging.info(
        f"Worst case output capacitor ripple, leakage, and total loss:"
        f"\n\tRipple loss: {np.max(points['PO_RIPPLE (W)']) :.3f} W"
        f"\n\tLeakage loss: {np.max(points['PO_LEAK (W)']) :.3f} W"
        f"\n\tTotal loss: {np.max(points['PO_TOT (W)']) :.3f} W"
    )

    logging.info(
        f"Worst case inductor conduction, core, and total loss:"
        f"\n\tConduction loss: {np.max(points['PL_COND (W)']) :.3f} W"
        f"\n\tCore loss: {np.max(points['PL_CORE (W)']) :.3f} W"
        f"\n\tTotal loss: {np.max(points['PL_TOT (W)']) :.3f} W"
    )

    return points


def map_passives(
    design, inp_caps, out_caps, inductor, ind_shape, ind_material, awg, output_path
):
    """_summary_
    map_passives
        map_ripple
        map_losses
        map_ind_thermals
    """
    sw = design["switches"]
    ci = design["input_cap"]
    co = design["output_cap"]
    l = design["inductor"]
    map = design["map"]
    sf = design["safety_factor"]

    # Get passive requirements
    (ci_reqs, co_reqs, l_reqs) = get_requirements(
        map["points"],
        sw["f_sw"],
        ci["v_pp"],
        co["v_pp"],
        l["r_l"],
        sf=sf,
    )

    def optimize_inductor(inductor):
        try:
            (
                _l,
                N,
                length_wire,
                area_wire,
                length_gap,
                p_cond,
                p_core,
            ) = size_inductor(ind_shape, ind_material, sw["f_sw"], *l_reqs)
            return pd.Series(
                [
                    _l * 1e6,
                    N,
                    length_wire,
                    area_wire,
                    length_gap * 1e6,
                    p_cond,
                    p_core,
                    p_core + p_cond,
                ]
            )
        except Exception as e:
            # print(e)
            return pd.Series([pd.NaT] * 8)

    inductor = inductor.copy()
    inductor[
        [
            "INDUCTANCE (uH)",
            "NUM_TURNS",
            "WIRE_LENGTH (m)",
            "WIRE_AREA (m^2)",
            "GAP_LENGTH (um)",
            "CONDUCTION_LOSS (W)",
            "CORE_LOSS (W)",
            "TOTAL_LOSS (W)",
        ]
    ] = inductor.apply(optimize_inductor, axis=1)

    logging.info(
        f"Input inductor selected:"
        f"\n\t{inductor.iloc[0]['PART_NAME']}"
        f"\n\twith {inductor.iloc[0]['NUM_TURNS']} turns "
        f"of {int(get_wire_gauge(awg, inductor.iloc[0]['WIRE_AREA (m^2)'] * 1e6))} gauge wire"
        f"\n\tand a core gap of {inductor.iloc[0]['GAP_LENGTH (um)'] / 2 / 1e3 :.1f} mm "
        f"per side of the core."
    )

    points = map_ripple(inp_caps, out_caps, inductor, map["points"], sw["f_sw"], output_path)
    points = map_losses(
        inp_caps, out_caps, inductor, ind_shape, ind_material, map["points"], sw["f_sw"], output_path
    )
    return points
