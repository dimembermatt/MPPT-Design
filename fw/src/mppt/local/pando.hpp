/**
 * @file pando.hpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief PandO MPPT algorithm driver.
 * @version 0.2.0
 * @date 2023-12-04
 * 
 * @copyright Copyright (c) 2023
 * 
 */
#pragma once
#include "../mppt.hpp"

class PandO final : public MPPT {
    public:
        PandO(void) : MPPT() {
            prev_array_voltage = 0.0;
            prev_array_power = 0.0;
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
            float array_power = array_voltage * array_current;

            // Get the discernment criteria
            float delta_array_voltage = array_voltage - prev_array_voltage;
            float delta_array_power = array_power - prev_array_power;

            #define STRIDE 0.1 // TODO: support variable stride
            if (delta_array_power > 0.0) {
                if (delta_array_voltage > 0.0) {
                    // Increase reference.
                    reference_voltage += STRIDE;
                } else if (delta_array_voltage < 0.0) {
                    // Decrease reference.
                    reference_voltage -= STRIDE;
                }
            } else {
                if (delta_array_voltage > 0.0) {
                    // Decrease reference.
                    reference_voltage -= STRIDE;
                } else if (delta_array_voltage < 0.0) {
                    // Increase reference.
                    reference_voltage += STRIDE;
                }
            }
            #undef STRIDE

            // Stash for next call.
            prev_array_voltage = array_voltage;
            prev_array_power = array_power;
        }

        void reset_state(void) {
            MPPT::reset_state();
            prev_array_voltage = 0.0;
            prev_array_power = 0.0;
        }
        
    protected:
        /** Required inputs. */
        float array_voltage;
        float array_current;
        float battery_voltage;
        float battery_current;

        /** Saved internal data. */
        float prev_array_voltage;
        float prev_array_power;
};
