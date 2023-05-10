"""_summary_
@file       solar_cell_nonideal_model.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Modeling an arbitrary solar cell.
@version    1.0.0
@date       2023-05-06
"""

import math as m
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import constants

k_b = constants.k
q = constants.e
i_sc_ref = 6.15
v_oc_ref = 0.721
G_ref = 1000
T_ref = 298.15
t_coeff_i_sc = 0.005
t_coeff_v_oc = -0.0022
n = 1.0
i_resolution = 0.001
margin = 0.0001


def model_nonideal_cell(g, t, r_s, r_sh, v):
    """_summary_
    Gets the current for a nonideal cell given input conditions using iterative
    solving.

    Args:
        g (double): Incident irradiance (W/m^2).
        t (double): Cell temperature (K).
        r_s (double): Series resistance (Ohms).
        r_sh (double): Shunt resistance (Ohms).
        v (double): Load voltage (V).

    Returns:
        double, [double] (OPT): Current (A) in either single or list form.
    """
    v_t = k_b * t / q
    i_sc = i_sc_ref * (g / G_ref) * (1 - t_coeff_i_sc * (T_ref - t))
    v_oc = v_oc_ref * (1 - t_coeff_v_oc * (T_ref - t)) + n * v_t * m.log(g / G_ref)
    i_0 = i_sc / (m.exp(v_oc / v_t) - 1)
    term_1 = i_sc * (r_sh + r_s) / r_sh  # TODO: check this term, not present in cubas

    # Single voltage measurement.

    prediction = 0.0
    new_l1_loss = 0.0
    travel_speed = i_resolution

    # 1. Calculate the seed output.
    left = prediction
    term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
    term_3 = -(v + prediction * r_s) / r_sh
    right = term_1 + term_2 + term_3

    # 2. Calculate the seed loss.
    l1_loss = abs(right - left)

    # 3. Iteratively solve for prediction.
    while True:
        # 8. Make a new prediction.
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 9. Calculate new L1 loss and determine whether to continue.
        new_l1_loss = abs(right - left)
        if new_l1_loss >= l1_loss:
            break
        l1_loss = new_l1_loss

    return prediction


def model(source):
    num_cells = source["num_cells"]
    r_s = source["r_s"]
    r_sh = source["r_sh"]

    v = [v for v in np.linspace(0.001, 0.721, 60)]
    i = [model_nonideal_cell(G_ref, T_ref, r_s, r_sh, _v) for _v in v]
    v = list(np.multiply(v, num_cells))

    return [v, i]

def map(source, output_path):
    v = source["i-v"][0]
    i = source["i-v"][1]
    p = [v * i for v, i in zip(v, i)]

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Array I-V/P-V Plot")
    ax1.plot(v, i)
    ax1.set_xlabel("Voltage (V)")
    ax1.set_ylabel("Current (A)")
    ax1.grid(True, "both", "both")
    ax2.plot(v, p)
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Power (W)")
    ax2.grid(True, "both", "both")
    plt.tight_layout()
    plt.savefig(output_path + "/00_source_model.png")
    plt.close()