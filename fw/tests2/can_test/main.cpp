/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Blackbody A/B CAN test. Verify that:
 *      - Loopback - HEARTBEAT CAN message can be sent and received in loopback configuration. 
 *      - Secondary device - HEARTBEAT CAN message can be sent and received between two devices.
 * @version 0.1.0
 * @date 2023-09-16
 * 
 * @copyright Copyright (c) 2023
 *
 * @note Pinout:
 *  - D1  | HEARTBEAT LED
 *  - D0  | TRACKING LED
 *  - D3  | ERROR LED
 * 
 *  - D2  | CAN_TX
 *  - D10 | CAN_RX
 *  - D4  | I2C_SDA to Blackbody C
 *  - D5  | I2C_SCL to Blackbody C
 *  - D11 | SPI_MISO to RTDs
 *  - D12 | SPI_MOSI to RTDs
 *  - D13 | SPI_SCLK to RTDs
 *  - A0  | SPI_CS_3 to RTDs
 *  - A1  | SPI_CS_7 to RTDs
 *  - A2  | SPI_CS_6 to RTDs
 *  - A3  | SPI_CS_2 to RTDs
 *  - A4  | SPI_CS_1 to RTDs
 *  - A5  | SPI_CS_5 to RTDs
 *  - A6  | SPI_CS_0 to RTDs
 *  - A7  | SPI_CS_4 to RTDs
 */
#include "mbed.h"
#define __LOOPBACK__ 0
#define __DEVICE_A__ 0

#define CAN_ID 0x01
#define CAN_TX D2
#define CAN_RX D10

static DigitalOut led_heartbeat(D1);
static DigitalOut led_tracking(D0);
static DigitalOut led_error(D3);
static CAN can(CAN_RX, CAN_TX);
static Ticker ticker_heartbeat;
static Ticker ticker_can;
static EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call an event to send a
 * pre-formed CAN message. 
 */
void handler_heartbeat(void);

/**
 * @brief Interupt triggered by receiving a CAN message to read the message.
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

int main(void)
{
    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

#if __LOOPBACK__ == 1
    // Loopback mode sends and receives CAN.
    can.mode(CAN::LocalTest);
    ticker_heartbeat.attach(&handler_heartbeat, 1000ms);
    can.attach(&handler_can, CAN::RxIrq);
#elif __DEVICE_A__ == 1
    // Non loopback mode device A only sends CAN.
    ticker_heartbeat.attach(&handler_heartbeat, 1000ms);
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
