/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter LED test. Verify that:
 *  1. Liveliness - verify that Error, Tracking, Heartbeat, CAN_TX/CAN_RX LEDs
 *     turn on and blink at 1 Hz.  
 * @version 0.2.0
 * @date 2023-12-02
 * @copyright Copyright (c) 2023
 *
 * @note For board revision v0.2.0.
 * @note See the TESTING.md document for detailed test instructions.
 * @note Pinout:
 *  - D1  | PA9  | HEARTBEAT LED
 *  - D0  | PA10 | TRACKING LED
 *  - D3  | PB0  | ERROR LED
 * 
 * @errata v0.2.0 hardware - PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
DigitalOut led_can_tx(D2);
DigitalOut led_can_rx(D10);

Ticker ticker_heartbeat;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to toggle LEDs.
 */
void handler_heartbeat(void);

int main(void) {
    set_time(0);

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. LED TEST.\n");

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;
    led_can_tx = 0;
    led_can_rx = 0;

    ticker_heartbeat.attach(&handler_heartbeat, 1000ms);
    queue.dispatch_forever();
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
    led_tracking = !led_tracking;
    led_error = !led_error;
    led_can_tx = !led_can_tx;
    led_can_rx = !led_can_rx;
}
