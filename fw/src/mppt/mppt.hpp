/**
 * @file mppt.hpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief MPPT algorithm driver.
 * @version 0.2.0
 * @date 2023-12-04
 * 
 * @copyright Copyright (c) 2023
 * 
 */
#pragma once

/**
 * @brief The MPPT class represents the base class of a large set of possible
 * algorithms used to manage the operating point of a photovoltaic array.
 * It can run a custom algorithm to take the input context, derive a new
 * setpoint, and return it to the user.
 */
class MPPT {
    public:
        /** @brief Construct a new MPPT object. */
        MPPT(void);

        /**
         * @brief Input relevant information required for the MPPT to make a decision.
         * 
         * @param args A pointer to an arbitrary number of arguments.
         */
        virtual void input_context(void *args);

        /** @brief Step the algorithm forward one iteration. */
        virtual void step_algorithm(void);

        /**
         * @brief Get the reference voltage of the photovoltaic array that the
         * system should be set to.
         * 
         * @return float Reference input voltage.
         */
        virtual float get_reference(void);

        /** @brief Reset the state of the algorithm. */
        virtual void reset_state(void);

    protected:
        /** 
         * The reference voltage associated with the current step of the
         * algorithm. 
         */ 
        float reference_voltage;
};
