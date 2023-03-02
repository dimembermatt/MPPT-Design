"""_summary_
@file       passives_design.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Calculate design parameters of passives (capacitors, inductors) for
            a DC-DC boost converter. 
@sources    - TI AN SLVA372D
            - TI AR SLVAF30
@version    0.0.0
@date       2023-03-02
"""

import matplotlib.pyplot as plt
import numpy as np


def get_passive_sizing(
    v_in_range, v_out_range, f_sw, r_ci_v, r_co_v, r_l_a, eff, model, num_cells, sf=0.25
):
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
    v_in_combos = np.linspace(v_in_range[0], v_in_range[2], num=25, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[2], num=25, endpoint=True)
    for v_in in v_in_combos:
        i_in = model(1000, 298.15, 0, 100, v_in / num_cells)
        p_in = v_in * i_in
        for v_out in v_out_combos:
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
            i_l_max.append(i_in + r_l_a_op)
            v_ci_max.append(v_in + r_ci_v)
            v_co_max.append(v_out + r_co_v_op)

    # Plot out switching frequency map.
    fig, axs = plt.subplots(2, 3, subplot_kw=dict(projection="3d"))
    axs[0, 0].scatter(x_v_in, y_v_out, np.multiply(ci_min, 1E6), c=ci_min)
    axs[0, 0].set_title("Min. Inp. Cap. Across I/O Mapping")
    axs[0, 0].set_xlabel("V_IN (V)")
    axs[0, 0].set_ylabel("V_OUT (V)")
    axs[0, 0].set_zlabel("Capacitance (uF)")

    axs[1, 0].scatter(x_v_in, y_v_out, v_ci_max, c=v_ci_max)
    axs[1, 0].set_title("Max. Inp. Cap. Voltage Across I/O Mapping")
    axs[1, 0].set_xlabel("V_IN (V)")
    axs[1, 0].set_ylabel("V_OUT (V)")
    axs[1, 0].set_zlabel("V_MAX (V)")

    axs[0, 1].scatter(x_v_in, y_v_out, np.multiply(co_min, 1E6), c=co_min)
    axs[0, 1].set_title("Min. Out. Cap. Across I/O Mapping")
    axs[0, 1].set_xlabel("V_IN (V)")
    axs[0, 1].set_ylabel("V_OUT (V)")
    axs[0, 1].set_zlabel("Capacitance (uF)")

    axs[1, 1].scatter(x_v_in, y_v_out, v_co_max, c=v_co_max)
    axs[1, 1].set_title("Max. Out. Cap. Voltage Across I/O Mapping")
    axs[1, 1].set_xlabel("V_IN (V)")
    axs[1, 1].set_ylabel("V_OUT (V)")
    axs[1, 1].set_zlabel("V_MAX (V)")

    axs[0, 2].scatter(x_v_in, y_v_out, np.multiply(l_min, 1E6), c=l_min)
    axs[0, 2].set_title("Min. Ind. Across I/O Mapping")
    axs[0, 2].set_xlabel("V_IN (V)")
    axs[0, 2].set_ylabel("V_OUT (V)")
    axs[0, 2].set_zlabel("Inductance (uH)")

    axs[1, 2].scatter(x_v_in, y_v_out, i_l_max, c=i_l_max)
    axs[1, 2].set_title("Max. Inductor Current Across I/O Mapping")
    axs[1, 2].set_xlabel("V_IN (V)")
    axs[1, 2].set_ylabel("V_OUT (V)")
    axs[1, 2].set_zlabel("Current (A)")

    plt.tight_layout()
    plt.savefig("capacitor_inductor_sizing_map.png")
    plt.show()

    ci_min = np.max(ci_min)
    co_min = np.max(co_min)
    l_min = np.max(l_min)

    ci_vdc_min = np.max(v_ci_max) * sf
    co_vdc_min = np.max(v_co_max) * sf
    l_a_min = np.max(i_l_max) * sf

    return (ci_min, co_min, l_min, ci_vdc_min, co_vdc_min, l_a_min)
