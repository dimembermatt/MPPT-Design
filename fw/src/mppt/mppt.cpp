/**
 * @file mppt.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief MPPT algorithm driver.
 * @version 0.2.0
 * @date 2023-12-04
 * 
 * @copyright Copyright (c) 2023
 * 
 */
#include "./mppt.hpp"

MPPT::MPPT(void) {
    reference_voltage = 0.0;
}

void MPPT::input_context(void *args) {

}

void MPPT::step_algorithm(void) {
    reference_voltage = 0.0;
}

float MPPT::get_reference(void) {
    return reference_voltage;
}

void MPPT::reset_state(void) {
    reference_voltage = 0.0;
}
