/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter PWM test. Verify that:
 *  1. Liveliness - verify that the gate driver can be actuated at a known
 *     frequency. 
 *  2. Correctness - verify that driving the gate driver to a specific input
 *     results in the correct state of each switch. 
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
 *  - D2  | PA12 | CAN_TX
 *  - D10 | PA11 | CAN_RX
 *
 *  - A3  | PA4  | PWM ENABLE
 *  - A4  | PA5  | PWM OUT
 * @note To load FastPWM: import http://os.mbed.com/users/Sissors/code/FastPWM/
 * @errata v0.2.0 PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"
#include "FastPWM.h"

#define PWM_FREQ 50000.0 // v0.2.0
// 0.0 - Force LOW SIDE switch closed, HIGH side switch open
// 1.0 - Force HIGH SIDE switch closed, LOW side switch open
#define PWM_DUTY 0.5
#define HEARTBEAT_FREQ 1.0

DigitalOut led_tracking(D0);
DigitalOut led_heartbeat(D1);
DigitalOut led_error(D3);
DigitalOut pwm_enable(A3);
FastPWM pwm_out(A2);

Ticker ticker_heartbeat;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to toggle the hartbeat
 * LED.
 */
void handler_heartbeat(void);

int main() {
    set_time(0);

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. PWM TEST.\n");

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / PWM_FREQ);
    pwm_out.write(1 - PWM_DUTY); // Inverted to get the correct output.
    pwm_enable = 1;

    led_tracking = 1;

    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
    queue.dispatch_forever();
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
}