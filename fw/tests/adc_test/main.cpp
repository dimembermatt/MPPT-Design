/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Reads in voltage and current measurements and applies a calibration
 * function.
 * @version 0.1
 * @date 2023-03-26
 * @note For board revision v0.1.0.
 * @copyright Copyright (c) 2023
 *
 */

#include "mbed.h"

AnalogIn arr_voltage_sensor(PA_4);
AnalogIn arr_current_sensor(PA_5);
AnalogIn batt_voltage_sensor(PA_7);
AnalogIn batt_current_sensor(PA_6);
DigitalOut led_heartbeat(PA_9);

Ticker ticker_heartbeat;
Ticker ticker_measure_adcs;

float calibrate_arr_v(float inp) {
    return inp;
}

float calibrate_arr_i(float inp) {
    return inp;
}

float calibrate_batt_v(float inp) {
    return inp;
}

float calibrate_batt_i(float inp) {
    return inp;
}

void heartbeat() { led_heartbeat = !led_heartbeat; }
void measure_adcs() {
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    printf("ARR: %f V, %f A\n", arr_v, arr_i);
    printf("BATT: %f V, %f A\n", batt_v, batt_i);
}


int main()
{
    ticker_heartbeat.attach(&heartbeat, 1000ms);
    ticker_measure_adcs.attach(&measure_adcs, 100ms);

    while (true) {
        ThisThread::sleep_for(1000ms);
    }
}
