/**
 * @file ic.hpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Incremental Conductance MPPT algorithm driver.
 * @version 0.2.0
 * @date 2023-12-04
 * 
 * @copyright Copyright (c) 2023
 * @note The implementation of this algorithm is based on the folowing paper:
 *
 * Incremental Conductance Based Maximum Power Point Tracking (MPPT)
 * for Photovoltaic System (Bhaskar et Lokanadham.)
 *
 * Section 5, Incremental Conductance MPPT
 *
 * Given a P-V curve of the solar cell, we can identify three region
 * of interest given its incremental versus instantaneous conductance:
 *
 *  dI/dV = - I/V   At MPP
 *  dI/dV > - I/V   Left of MPP
 *  dI/dV < - I/V   Right of MPP
 *
 * The algorithm is then fairly straightforward. Identify which region
 * of interest we are in, and move to the direction of the MPP using a
 * stride function.
 */
#pragma once
#include "math.h"
#include "../mppt.hpp"

class IC final : public MPPT {
    public:
        IC(void) : MPPT() {
            prev_array_voltage = 0.0;
            prev_array_current = 0.0;
        }

        void input_context(void *args) {
            #define INPUT_VOLTAGE ((float *) args)[0]
            #define INPUT_CURRENT ((float *) args)[1]
            #define OUTPUT_VOLTAGE ((float *) args)[2]
            #define OUTPUT_CURRENT ((float *) args)[3]

            array_voltage = INPUT_VOLTAGE;
            array_current = INPUT_CURRENT;
            battery_voltage = OUTPUT_VOLTAGE;
            battery_current = OUTPUT_CURRENT;

            #undef INPUT_VOLTAGE
            #undef INPUT_CURRENT
            #undef OUTPUT_VOLTAGE
            #undef OUTPUT_CURRENT
        }

        void step_algorithm(void) {
            // Get the discernment criteria
            float delta_array_current = array_current - prev_array_current;
            float delta_array_voltage = array_voltage - prev_array_voltage;

            #define STRIDE 0.1 // TODO: support variable stride
            #define ERROR 0.01 // TODO: support variable error
            if (abs(delta_array_current * array_voltage + array_current * delta_array_voltage) < ERROR) {
                // At MPP
            } else if ((delta_array_current * array_voltage + array_current * delta_array_voltage) > ERROR) {
                // Left of MPP
                reference_voltage += STRIDE;
            } else if ((delta_array_current * array_voltage + array_current * delta_array_voltage) < -ERROR) {
                // Right of MPP
                reference_voltage -= STRIDE;
            } else {
                // TODO: raise exception.
            }
            #undef STRIDE
            #undef ERROR

            // Stash for next call.
            prev_array_voltage = array_voltage;
            prev_array_current = array_current;
        }

        void reset_state(void) {
            MPPT::reset_state();
            prev_array_voltage = 0.0;
            prev_array_current = 0.0;
        }
        
    protected:
        /** Required inputs. */
        float array_voltage;
        float array_current;
        float battery_voltage;
        float battery_current;

        /** Saved internal data. */
        float prev_array_voltage;
        float prev_array_current;
};
