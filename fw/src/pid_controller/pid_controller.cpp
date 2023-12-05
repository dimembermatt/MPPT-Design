/**
 * @file pid_controller.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief PID controller driver.
 * @version 0.2.0
 * @date 2021-12-04
 * 
 * @copyright Copyright (c) 2023
 * 
 */

/** Device Specific imports. */
#include "./pid_controller.hpp"

PIDController::PIDController(float min, float max, float p, float i, float d) {
    min_output = min;
    max_output = max;
    p_coeff = p;
    i_coeff = i;
    d_coeff = d;

    prev_error = 0.0;
    sum_error = 0.0;
    delta_error = 0.0;
}

float PIDController::step_pid(float target, float actual) {
    // Calculate components.
    float error = target - actual;
    sum_error += error;
    delta_error = error - prev_error;
    prev_error = error;

    // Calculate output.
    float output = (p_coeff * error) + (i_coeff * sum_error) + (d_coeff * delta_error);

    // Constrain the output.
    if (output < min_output) output = min_output;
    if (output > max_output) output = max_output;

    return output;
}

void PIDController::reset_state(void) {
    prev_error = 0.0;
    sum_error = 0.0;
    delta_error = 0.0;
}
