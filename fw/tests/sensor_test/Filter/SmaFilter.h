/**
 * Maximum Power Point Tracker Project
 * 
 * File: SmaFilter.h
 * Author: Matthew Yu
 * Organization: UT Solar Vehicles Team
 * Created on: September 19th, 2020
 * Last Modified: 06/08/21
 * 
 * File Description: This header file implements the SmaFilter class, which
 * is a derived class from the parent Filter class. SMA stands for Simple Moving
 * Average.
 * 
 * Sources:
 * https://hackaday.com/2019/09/06/sensor-filters-for-coders/
 */
#pragma once
#include "Filter.h"

class SmaFilter final : public Filter {
    public:
        /** Default constructor for a SmaFilter object. 10 sample size. */
        SmaFilter(void) : Filter(10) {
            mDataBuffer = new float[mMaxSamples];
            mIdx = 0;
            mNumSamples = 0;
            mSum = 0;
        }

        /**
         * Constructor for a SmaFilter object.
         * 
         * @param[in] maxSamples Number of samples that the filter should 
         *                       hold at maximum at any one time.
         * @precondition maxSamples is a positive number.
         */
        SmaFilter(const uint16_t maxSamples) : Filter(maxSamples) {
            mDataBuffer = new float[mMaxSamples];
            mIdx = 0;
            mNumSamples = 0;
            mSum = 0;
        }

        void addSample(const float sample) override { 
            /* Check for exception. */
            if (mDataBuffer == nullptr) { return; }
            
            /* Saturate counter at max samples. */
            if (mNumSamples < mMaxSamples) {
                ++mNumSamples;
                mSum += sample;
            } else {
                /* Add the new value but remove the value at the 
                   current index we're overwriting. */
                mSum += sample - mDataBuffer[mIdx];
            }
            mDataBuffer[mIdx] = sample;
            mIdx = (mIdx + 1) % mMaxSamples;
        }

        float getResult(void) const override { 
            /* Check for exception. */
            if (mDataBuffer == nullptr || mNumSamples == 0) { return 0.0; }
            return mSum / mNumSamples;
        }

        void clear(void) override {
            mNumSamples = 0;
            mIdx = 0;
            mSum = 0;
        }

        void shutdown(void) override { delete[] mDataBuffer; }

    private:
        /** Data Buffer. */
        float * mDataBuffer;

        /** Number of samples in the buffer. */
        uint16_t mNumSamples;

        /** Current index in the buffer. */
        uint16_t mIdx;

        /** Sum of the current window of data points. */
        float mSum;
};
