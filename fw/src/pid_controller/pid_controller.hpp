/**
 * @file PIDController.hpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief PID controller driver.
 * @version 0.2.0
 * @date 2021-12-04
 * 
 * @copyright Copyright (c) 2023
 * 
 */
#pragma once

/**
 * @brief The PIDController class implements a simple PID controller used to
 * manage the operating point of a system.
 */
class PIDController {
    public:
        /**
         * @brief Construct a new PIDController object.
         * 
         * @param min Minimum possible output.
         * @param max Maximum possible output.
         * @param p Proportional term coefficient.
         * @param i Integral term coefficient.
         * @param d Derivative term coefficient.
         */
        PIDController(float min, float max, float p, float i, float d);

        /**
         * @brief Step the PID loop forward one iteration.
         * 
         * @param target Target output of system.
         * @param actual Measured output of system.
         * @return float New reference signal to drive the system.
         */
        float step_pid(float target, float actual);

        /** @brief Reset the state of the controller. */
        void reset_state(void);

    private:
        /** Configuration values. */
        float min_output;
        float max_output;
        float p_coeff;
        float i_coeff;
        float d_coeff;

        /** Savestate values.*/
        float prev_error;
        float sum_error;
        float delta_error;

};
