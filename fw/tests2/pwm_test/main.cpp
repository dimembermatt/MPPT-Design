/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter pwm test. Verify that:
 *      - When PWM held LOW, ENABLE is ON
 *          - Shorts across body diode of HIGH SIDE FET from ARR+ to BATT+, open other direction (TPs VSW, VBATT+)
 *          - Shorts across LOW SIDE FET in both directions (TPs VSW, GND)
 *      - When PWM held HIGH, ENABLE is ON
 *          - Shorts across body diode of LOW SIDE FET from GND to ARR+, open other direction (TPs GND, VSW)
 *          - Shorts across HIGH SIDE FET in both directions (TPs VSW, VBATT+)
 *      - When ENABLE is OFF
 *          - Shorts across body diode of HIGH SIDE FET from ARR+ to BATT+, open other direction (TPs VSW, VBATT+)
 *          - Shorts across body diode of LOW SIDE FET from GND to ARR+, open other direction (TPs GND, VSW)
 *      - When PWM is set to 50% duty, the logic analyzer verifies as much on SW1 and GND, and SW2 and VSW.
 * @version 0.1.0
 * @date 2023-09-16
 *
 * @copyright Copyright (c) 2023
 *
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
 * 
 * @errata PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);

DigitalOut pwm_enable(A3);
PwmOut pwm_out(A2);

Ticker ticker_heartbeat;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call an event to send a
 * pre-formed CAN message. 
 */
void handler_heartbeat(void);

int main()
{
    set_time(0);
    ThisThread::sleep_for(1000ms);
    printf("PWM Test\n");

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / 100000.0); // 100 kHz

    pwm_enable = 1;
    // 0.0 - Force LOW SIDE switch closed, HIGH side switch open
    // 1.0 - Force HIGH SIDE switch closed, LOW side switch open
    pwm_out.write(0.5);

    led_tracking = 1;

    ticker_heartbeat.attach(&handler_heartbeat, 100ms);
    queue.dispatch_forever();
    while(true);
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
}