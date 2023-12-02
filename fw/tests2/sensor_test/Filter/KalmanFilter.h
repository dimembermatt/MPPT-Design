/**
 * Maximum Power Point Tracker Project
 * 
 * File: KalmanFilter.h
 * Author: Matthew Yu
 * Organization: UT Solar Vehicles Team
 * Created on: September 20th, 2020
 * Last Modified: 06/08/21
 * 
 * File Description: This header file implements the KalmanFilter class, which
 * is a derived class from the parent Filter class.
 * 
 * Source: https://www.kalmanfilter.net/kalman1d.html
 */
#pragma once
#include "Filter.h"
#include <stdio.h>

class KalmanFilter final : public Filter {
    public:
        /** Default constructor for a KalmanFilter object. 10 sample size. */
        KalmanFilter(void) : Filter(10) {            
            mEstimate = 10.0;
            mEu = 225;
            mMu = 25;
            mQ = 0.15;
        }
        
        /**
         * Constructor for a KalmanFilter object.
         * 
         * @param[in] maxSamples Number of samples that the filter should hold at maximum 
         *      at any one time.
         * @precondition maxSamples is a positive number.
         */
        KalmanFilter(const uint16_t maxSamples) : Filter(maxSamples) {
            mEstimate = 10.0;
            mEu = 225;
            mMu = 25;
            mQ = 0.15;
        }

        /**
         * Constructor for a KalmanFilter object.
         * 
         * @param[in] maxSamples Number of samples that the filter should hold at 
         *                       maximum at any one time.
         * @param[in] initialEstimate Initial guess of a sensor sample value. A 
         *                       best guess would be at STC (i.e. Temp sensor:
         *                       25.0 C, 128 cell subarray - .65V each: 85.0 V,
         *                       5.5 A from a subarray).
         * @param[in] estimateUncertainty Estimate uncertainty variance. Play 
         *                       around with this value. Decreases over time by
         *                       itself after initialization.
         * @param[in] measurementUncertainty Uncertainty of the input measurement. 
         *                       Typically listed on the datasheet but may need
         *                       to be determined for custom builds (i.e. RTD to
         *                       ADC).
         * @param[in] processNoiseVariance Measurement of how good we think our model 
         *                       is. Recommended range is 0.15 to 0.001. Play
         *                       around with this value.
         * @precondition maxSamples is a positive number.
         */
        KalmanFilter(
            const uint16_t maxSamples, 
            const float initialEstimate,
            const float estimateUncertainty,
            const float measurementUncertainty,
            const float processNoiseVariance
        ) : Filter(maxSamples) {
            mEstimate = initialEstimate;
            mEu = estimateUncertainty;
            mMu = measurementUncertainty;
            mQ = processNoiseVariance;
        }

        void addSample(const float sample) override { 
            /* Kalman Gain. */
            double K = mEu / (mEu + mMu);
            /* Estimate update (state update). */
            mEstimate = mEstimate + K * (sample - mEstimate);
            /* Estimate uncertainty. */
            mEu = (1-K) * mEu;
            /* Predict estimate. */
            // mEstimate = mEstimate;
            /* Predict estimate uncertainty. */
            mEu = mEu + mQ;
        }

        float getResult(void) const override { return mEstimate; }

        void clear(void) override {
            mEstimate = 10.0;
            mEu = 225;
            mMu = 25;
            mQ = 0.15;
        }

    private:
        /** Guess. */
        float mEstimate;

        /** Estimate uncertainty (variance). */
        float mEu;

        /** Measurement uncertainty. */
        float mMu;

        /** Process noise variance. */
        float mQ;
};


void TEST() {
    printf("Hello World Test\n");
    // setup
    KalmanFilter filter(5); // 5 sample buffer
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