/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Turns on the LEDs to determine whether they are operable.
 * @version 0.1
 * @date 2023-03-26
 * @note For board revision v0.1.0.
 * @copyright Copyright (c) 2023
 *
 */

#include "DigitalOut.h"
#include "ThisThread.h"
#include "mbed.h"
#include <cstdio>

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut led_error(PB_0);

Ticker ticker_heartbeat;

void heartbeat() { led_heartbeat = !led_heartbeat; }

int main()
{
    ticker_heartbeat.attach(&heartbeat, 1000ms);
    led_tracking = 1;
    led_error = 1;

    while (true) {
        ThisThread::sleep_for(1000ms);
    }
}
