/**
 * Maximum Power Point Tracker Project
 * 
 * File: Filter.cpp
 * Author: Matthew Yu
 * Organization: UT Solar Vehicles Team
 * Created on: September 19th, 2020
 * Last Modified: 06/06/21
 * 
 * File Description: This implementation file describes the Filter class, which
 * is an inherited class that allows callers to filter and denoise input data.
 */
#include "Filter.h"

Filter::Filter(void) {
    mMaxSamples = 10;
    mCurrentVal = 0;
}

Filter::Filter(const uint16_t maxSamples) {
    mMaxSamples = maxSamples;
    mCurrentVal = 0;
}

void Filter::addSample(const float val) { mCurrentVal = val; }

float Filter::getResult(void) const { return mCurrentVal; }

void Filter::clear(void) { mCurrentVal = 0; }

void Filter::shutdown(void) { return; }
