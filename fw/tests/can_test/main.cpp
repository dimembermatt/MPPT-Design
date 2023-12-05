/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter CAN test. Verify that:
 *  1. Loopback - HEARTBEAT CAN message can be sent and received in loopback
 *     configuration. 
 *  2. With a secondary device - HEARTBEAT CAN message can be sent and received
 *     between two devices. 
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
 * @errata v0.2.0 PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"
#define __LOOPBACK__ 0
#define __DEVICE_A__ 1

#define CAN_ID 0x01
#define CAN_TX D2
#define CAN_RX D10
#define HEARTBEAT_FREQ 1.0

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
CAN can(CAN_RX, CAN_TX);

Ticker ticker_heartbeat;
Ticker ticker_can;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call event
 * event_send_can and toggle the heartbeat LED.
 */
void handler_heartbeat(void);

/**
 * @brief Interrupt triggered by a CAN RX IRQ to call event
 * event_receive_can.
 */
void handler_can(void);

/**
 * @brief Event to send a pre-formed CAN message.
 */
void event_send_can(void);

/**
 * @brief Event to receive a pre-formed CAN message.
 */
void event_receive_can(void);

int main(void) {
    set_time(0);

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. CAN TEST.\n");

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

#if __LOOPBACK__ == 1
    // Loopback mode sends and receives CAN.
    can.mode(CAN::LocalTest);
    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
    can.attach(&handler_can, CAN::RxIrq);
#elif __DEVICE_A__ == 1
    // Non loopback mode device A only sends CAN.
    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
#else
    // Non loopback mode device B only receives CAN.
    can.attach(&handler_can, CAN::RxIrq);
#endif
    queue.dispatch_forever();
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
    queue.call(&event_send_can);
}

void handler_can(void) {
    queue.call(&event_receive_can);
}

void event_send_can(void) {
    static char counter = 0;
    CANMessage message(CAN_ID, &counter, 1);
    if (can.write(message)) {
        led_error = !led_error;
        ++counter;
    }
}

void event_receive_can(void) {
    CANMessage msg;
    if (can.read(msg)) {
        led_tracking = !led_tracking;
    }
}
