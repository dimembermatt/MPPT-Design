/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Blackbody A/B liveliness test. Verify that Error, Tracking, Heartbeat, 
 *      CAN_TX/CAN_RX LEDs turn on. 
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

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
DigitalOut led_can_tx(D2);
DigitalOut led_can_rx(D10);

Ticker ticker_heartbeat;
void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
    led_tracking = !led_tracking;
    led_error = !led_error;
    led_can_tx = !led_can_tx;
    led_can_rx = !led_can_rx;
}

int main(void)
{
    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;
    led_can_tx = 0;
    led_can_rx = 0;

    ticker_heartbeat.attach(&handler_heartbeat, 1000ms);

    while (true);
}

