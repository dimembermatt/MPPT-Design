/**
 * @file fuzzy.hpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Fuzzy Logic MPPT algorithm driver.
 * @version 0.2.0
 * @date 2023-12-04
 * 
 * @copyright Copyright (c) 2023
 * @note     The Fuzzy Logic class is a derived class of LocalMPPTAlgorithm. 
 * This particular verstion attempts to replicate Takun et al and has two input variables:
 * - change in power
 * - change in current
 *
 * These two input variables are classified by their respective membership
 * functions (MFs).
 * 
 * The power membership function defines 5 terms
 * - NB - Negative Big     | [, -10%]
 * - NS - Negative Small   | (-10%, -3%]
 * - ZE - Zero             | (-3%, 3%)
 * - PS - Positive Small   | [3%, 10%)
 * - PB - Positive Big     | [10%, ]
 * 
 * And the current membership function defines 3 terms:
 * - N - Negative          | [, -1%]
 * - Z - Zero              | (-1%, 1%)
 * - P - Positive          | [1%, ]
 * 
 * The rule table for the juxtaposition of both MFs is as follows, and is
 * strictly arbitrary. The output term is the change in the reference voltage.
 * 
 * Fuzzy Rule         dP/dV
 *               NB | NS | ZE | PS | PB
 *         N   | NB | NS | PS | PS | PB
 * dI/dV   Z   | PB | PS | ZE | NS | NB
 *         P   | PB | PS | NS | NS | NB
 * 
 * Where the output set corresponds to the following values:
 * - NB - Negative Big     | -5%
 * - NS - Negative Small   | -1%
 * - ZE - Zero             | 0%
 * - PS - Positive Small   | 1%
 * - PB - Positive Big     | 5%
 * 
 * Beyond the current scope of this validation and proof of concept paper are
 * following additions:
 *
 * - The input variable set can be further expanded to include:
 *     - change in voltage
 *     - change in temperature
 *     - change in irradiance
 * - The membership functions can have a wider set size, perhaps 5 rules per
 *   input.
 * - The membership function shapes can also be varied (triangular, trapezoial,
 *   sigmoidal, etc).
 * - The rule table values can be optimized using brute force automation
 *   testing and/or machine learning approaches.
 *   
 * Fuzzy Logic utilizes the rule table to defuzzify the inputs and generate an
 * output. This can be considered a form of adaptive hill climbing algorithm in
 * that it utilizes the change of power and change of voltage over time to
 * determine the direction of movement and stride of the next reference 
 * voltage.
 */
#pragma once
#include "../mppt.hpp"
#include <stdint.h>

#define DIM_IN0_LEN 5
#define DIM_IN1_LEN 3
#define DIM_OUT_LEN 5

class Fuzzy final : public MPPT {
    public:
        Fuzzy(void) : MPPT() {
            has_started = false;
            prev_array_current = 0.0;
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
            if (!has_started) {
                reference_voltage = 0.0;
                has_started = true;
            } else {
                // Get the discernment criteria
                float array_power = array_voltage * array_current;
                float delta_array_current = array_current = prev_array_current;
                float delta_array_power = array_power - prev_array_power;
                
                // Input 0 is the proportion of the change of power relative to
                // the max power.
                float in_0 = delta_array_power * 100 / max_power;

                // Input 1 is the proportion of the change of current relative
                // to the max current.
                float in_1 = delta_array_current * 100 / max_current;

                // Get axis 0 index of delta power ruleset.
                uint8_t idx_dim_in_0 = 0;
                for (uint8_t i = 0; i < DIM_IN0_LEN; ++i) {
                    if (in_0 > input_0[i][0] && in_0 < input_0[i][1])
                        idx_dim_in_0 = i;
                }

                // Get axis 1 index of delta current ruleset.
                uint8_t idx_dim_in_1 = 0;
                for (uint8_t i = 0; i < DIM_IN1_LEN; ++i) {
                   if (in_1 > input_1[i][0] && in_1 < input_1[i][1])
                        idx_dim_in_1 = i;
                }

                // Get ruleset output index. Row column major.
                uint8_t idx_out = ruleset[idx_dim_in_1][idx_dim_in_0];

                // Get ruleset output.
                float delta_array_voltage = output[idx_out];

                // Update reference.
                reference_voltage += delta_array_voltage;
            }
        }

        void reset_state(void) {
            MPPT::reset_state();
            has_started = false;
            prev_array_current = 0.0;
            prev_array_power = 0.0;
        }
        
    protected:
        bool has_started;

        /** Internal constants. */
        float max_power = 400; // W
        float max_current = 8; // A

        /** Required inputs. */
        float array_voltage;
        float array_current;
        float battery_voltage;
        float battery_current;

        /** Saved internal data. */
        float prev_array_current;
        float prev_array_power;

        /** Ruleset. */
        float input_0[DIM_IN0_LEN][2] = {{-100, -10}, {-10, -3}, {-3, 3}, {3, 10}, {10, 100}};
        float input_1[DIM_IN1_LEN][2] = {{-100, -1}, {-1, 1}, {1, 100}};
        uint8_t ruleset[DIM_IN1_LEN][DIM_IN0_LEN] = {
            {1, 1, 1, 3, 4},
            {3, 3, 2, 3, 4},
            {4, 3, 3, 1, 1}
        }; // Note that we have no calls for output idx 0. No big backwards traversal.
        float output[DIM_OUT_LEN] = {-0.04, -0.02, 0.01, 0.02, 0.04};
};

#undef DIM_IN0_LEN
#undef DIM_IN1_LEN
#undef DIM_OUT_LEN
