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

import math as m
import sys

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
    v_in_combos = np.linspace(v_in_range[0], v_in_range[2], num=50, endpoint=True)
    v_out_combos = np.linspace(v_out_range[0], v_out_range[2], num=50, endpoint=True)
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
    l_a_min = np.max(i_l_max) * 1.05 # override * sf

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

def get_capacitor_loss():
    pass

def get_capacitor_esr(c, f_sw, df):
    ESR = df / (2 * m.pi * f_sw * c)
    return ESR

def get_capacitor_impedance(c, f_sw):
    return 1 / (2 * m.pi * f_sw * c)

def get_capacitor_v_rms(v_max):
    return v_max / (2 * m.sqrt(2))

def get_capacitor_i_rms(v_rms, z):
    return v_rms / z

def get_capacitor_pow_diss(i_rms, esr):
    return i_rms ** 2 * esr

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

    # @ 125 V bias, 125 C, 109 kHz
    c = 1.034 * 1E-6 # uF
    esr = 5.4 * 1E-3 # mO
    i_rms = 2.75 # A

    p_dis = get_capacitor_pow_diss(i_rms, esr)
    print(f"P_DIS: {p_dis} W")

    # @ 125 V bias, 125 C, 102 kHz
    c = 4.344 * 1E-6 # uF
    esr = 5.126 * 1E-3 # mO
    i_rms = (6.15 + 2.75/2) / m.sqrt(2) # A

    p_dis = get_capacitor_pow_diss(i_rms, esr)
    print(f"P_DIS: {p_dis} W")