/**
 * Maximum Power Point Tracker Project
 * 
 * File: Filter.h
 * Author: Matthew Yu
 * Organization: UT Solar Vehicles Team
 * Created on: September 19th, 2020
 * Last Modified: 06/06/21
 * 
 * File Description: This header file describes the Filter class, which is an
 * inherited class that allows callers to filter and denoise input data.
 * The Filter class is a concrete class that acts as a passthrough.
 */
#pragma once
#include <stdint.h>

class Filter {
    public:
        /** Default constructor for a filter object. 10 sample size. */
        Filter(void);

        /**
         * constructor for a filter object.
         * 
         * @param[in] maxSamples Number of samples that the filter should hold
         *                       at maximum at any one time.
         */
        Filter(const uint16_t maxSamples);

        /**
         * Adds a sample to the filter and updates calculations.
         * 
         * @param[in] val Input value to calculate filter with.
         */
        virtual void addSample(const float val);

        /**
         * Returns the filtered result of the input data.
         * 
         * @return Filter output.
         */
        virtual float getResult(void) const;

        /** Clears data stored in the filter. */
        virtual void clear(void);

        /** Deallocates constructs in the filter for shutdown. */
        virtual void shutdown(void);

    protected:
        /** Maximum number of samples that can be held. */
        uint16_t mMaxSamples;

        /** Current value of the filter output. */
        float mCurrentVal;
};
