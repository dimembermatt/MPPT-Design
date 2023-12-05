/**
 * Maximum Power Point Tracker Project
 * 
 * File: EmaFilter.h
 * Author: Matthew Yu
 * Organization: UT Solar Vehicles Team
 * Created on: September 20th, 2020
 * Last Modified: 06/08/21
 * 
 * File Description: This header file implements the EmaFilter class, which
 * is a derived class from the parent Filter class. EMA stands for Exponential
 * Moving Average.
 * 
 * Sources:
 * https://hackaday.com/2019/09/06/sensor-filters-for-coders/
 * https://www.norwegiancreations.com/2015/10/tutorial-potentiometers-with-arduino-and-filtering/
 * https://www.norwegiancreations.com/2016/08/double-exponential-moving-average-filter-speeding-up-the-ema/
 */
#pragma once
#include "Filter.h"
#include <stdio.h>

class EmaFilter final : public Filter {
    public:
        /** Default constructor for a EmaFilter object. 10 sample size. */
        EmaFilter(void) : Filter(10) {
            mAvg = 0;
            mAlpha = 0.2;
        }
        
        /**
         * Constructor for a EmaFilter object.
         * 
         * @param[in] maxSamples Number of samples that the filter should hold at 
         *                       maximum at any one time.
         * @param[in] alpha A constant from [0, 1] inclusive that indicates the
         *                  weight decline of each progressive sample.
         * @precondition maxSamples is a positive number.
         */
        EmaFilter(const uint16_t maxSamples, const float alpha) : Filter(maxSamples) {
            mAvg = 0;
            mAlpha = alpha;
        }

        void addSample(const float sample) override { 
            mAvg = (1-mAlpha) * mAvg + mAlpha * sample;
        }

        float getResult(void) const override { return mAvg; }

        void clear(void) override { mAvg = 0; }

    private:
        /** Weighted average of the data points. */
        float mAvg;

        /** Alpha constant for weight depreciation. */
        float mAlpha;
};

void TEST() {
    printf("Hello World Test\n");
    // setup
    EmaFilter filter(5, .2); // 5 sample buffer
    // add 20 samples, increasing linearly by 10, and then some noisy 100s every 5 cycles.
    for (uint16_t i = 0; i < 20; i++) {
        if (i%5 == 0) { filter.addSample(100); } 
        else { filter.addSample(i*10.0); }
    
        // read the filter output at every point
        printf("output:\t%f\n\n", filter.getResult());
    }
    // shutdown
    filter.shutdown();
}
