"""_summary_
"""

import math as m
import sys

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
i_resolution = 0.0025
margin = 0.0005


def model_nonideal_cell(g, t, r_s, r_sh, v, i=None):
    """_summary_
    Gets the current for a nonideal cell given input conditions using iterative
    solving.

    Args:
        g (double): Incident irradiance (W/m^2).
        t (double): Cell temperature (K).
        r_s (double): Series resistance (Ohms).
        r_sh (double): Shunt resistance (Ohms).
        v (double): Load voltage (V).
        i (double): Previous guess.

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
    # 1. Generate initial seed/prediction.
    #    Reuse the previous layer prediction to attempt to reduce number of
    #    steps.
    if i is not None:
        prediction = i

    # 2. Calculate the seed output.
    left = prediction
    term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
    term_3 = -(v + prediction * r_s) / r_sh
    right = term_1 + term_2 + term_3

    # 3. Calculate the seed loss.
    l1_loss = abs(right - left)

    # 4. Determine initial direction by stepping one way.
    if i is not None:
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 5. Calculate losses from first step.
        new_l1_loss = abs(right - left)

        # 6. Correct direction given first step losses.
        if l1_loss < new_l1_loss:
            # If we're going in the wrong direction, reverse the prediction and
            # travel the other way.
            prediction -= travel_speed
            travel_speed = -travel_speed
        else:
            # If we're going in the right direction, keep the prediction.
            l1_loss = new_l1_loss

    # 7. Iteratively solve for prediction.
    while True:
        # 8. Make a new prediction.
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 9. Calculate new L1 loss and determine whether to continue.
        new_l1_loss = abs(right - left)
        is_stable = True
        if new_l1_loss + margin < l1_loss:
            # If we're going in the right direction, keep going.
            l1_loss = new_l1_loss
            is_stable = False
        elif new_l1_loss > l1_loss + margin:
            # If we're going in the wrong direction, back up.
            travel_speed = -travel_speed
            is_stable = False
        else:
            # If we're stagnant, give up.
            travel_speed = 0.0

        if is_stable:
            break

    return prediction


def model_nonideal_cell_many(v, g, t, r_s, r_sh, i=None):
    """_summary_
    Gets the current for a nonideal cell given input conditions using iterative
    solving.

    Args:
        v ([float]): Load voltages (V).
        g (float): Incident irradiance (W/m^2).
        t (float): Cell temperature (K).
        r_s (float): Series resistance (Ohms).
        r_sh (float): Shunt resistance (Ohms).

    Returns:
        [float]: Cell currents (A)
    """
    v_t = k_b * t / q
    i_sc = i_sc_ref * (g / G_ref) * (1 - t_coeff_i_sc * (T_ref - t))
    v_oc = v_oc_ref * (1 - t_coeff_v_oc * (T_ref - t)) + n * v_t * m.log(g / G_ref)
    i_0 = i_sc / (m.exp(v_oc / v_t) - 1)
    term_1 = i_sc * (r_sh + r_s) / r_sh  # TODO: check this term, not present in cubas

    # Single voltage measurement.

    prediction = np.array([0.0] * len(v))
    new_l1_loss = 0.0
    travel_speed = np.array([i_resolution] * len(v))
    # 1. Generate initial seed/prediction.
    #    Reuse the previous layer prediction to attempt to reduce number of
    #    steps.
    if i is not None:
        prediction = i

    # 2. Calculate the seed output.
    left = prediction
    term_2 = -i_0 * (np.exp((v + prediction * r_s) / v_t) - 1)
    term_3 = -(v + prediction * r_s) / r_sh
    right = term_1 + term_2 + term_3

    # 3. Calculate the seed loss.
    l1_loss = np.abs(right - left)

    # 4. Determine initial direction by stepping one way.
    if i is not None:
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (np.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 5. Calculate losses from first step.
        new_l1_loss = np.abs(right - left)

        # 6. Correct direction given first step losses.
        for idx, [_l1_loss, _new_l1_loss] in enumerate(zip(l1_loss, new_l1_loss)):
            if _l1_loss < _new_l1_loss:
                # If we're going in the wrong direction, reverse the prediction and
                # travel the other way.
                prediction[idx] -= travel_speed[idx]
                travel_speed[idx] = -travel_speed[idx]
            else:
                # If we're going in the right direction, keep the prediction.
                l1_loss[idx] = new_l1_loss[idx]

    # 7. Iteratively solve for prediction.
    while True:
        # 8. Make a new prediction for those who have a travel_speed.
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (np.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 9. Calculate new L1 loss and determine whether to continue.
        new_l1_loss = np.abs(right - left)
        is_stable = True
        for idx, [_l1_loss, _new_l1_loss] in enumerate(zip(l1_loss, new_l1_loss)):
            if _new_l1_loss + margin < _l1_loss:
                # If we're going in the right direction, keep going.
                l1_loss[idx] = new_l1_loss[idx]
                is_stable = False
            elif _new_l1_loss > _l1_loss + margin:
                # If we're going in the wrong direction, back up.
                travel_speed[idx] = -travel_speed[idx]
                is_stable = False
            else:
                # If we're stagnant, give up.
                travel_speed[idx] = 0.0

        if is_stable:
            break

    return prediction
