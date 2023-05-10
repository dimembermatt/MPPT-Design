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
DigitalOut pwm_enable(PA_3);
PwmOut pwm_out(PA_1);
Ticker ticker_heartbeat;
Ticker ticker_measure_areaddcs;

float calibrate_arr_v(float inp) {
    if (inp < 1.0) return inp * 114.0;
    else return 114.0;
}

float calibrate_arr_i(float inp) {
    if (inp < 1.0) return inp * 5.79 + 0.0042;
    else return 5.79;
}

float calibrate_batt_v(float inp) {
    if (inp < 1.0) return inp * 168.0 + 0.0393;
    else return 168.0;
}

float calibrate_batt_i(float inp) {
    if (inp < 1.0) return inp * 5.8 + 0.0167;
    else return 5.8;
}

void heartbeat() { led_heartbeat = !led_heartbeat; }


int main()
{
    set_time(1679957180);
    pwm_enable = 0; 
    pwm_out.period(1.0 / 100000.0); // 100 kHz
    pwm_out.write(1.0); 
    /**
     * Testing:
     * - V_ARR: enable off, supply 0 - 80 V to input and compare expected (multimeter) with received.
     * - V_BATT: enable off, supply 0 - 130 V to output and compare expected with received.
     * - I_ARR, I_BATT: enable on, 100% duty to short high side switch, tie output to short current. 
     *   Supply 0 - 6 A to input and compare expected (multimeter on both sides) with received.
     * Note that there is ~1.29V drop on some conditions (enable = 0, duty = 1.0). This may be an issue.
     */
    ticker_heartbeat.attach(&heartbeat, 1000ms);

    while (true) {
        ThisThread::sleep_for(1000ms);
        time_t seconds = time(NULL);
        float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
        float arr_i = calibrate_arr_i(arr_current_sensor.read());
        float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
        float batt_i = calibrate_batt_i(batt_current_sensor.read());

        // CSV format for later analysis.
        printf("%u,%f,%f,%f,%f\n", (unsigned int) seconds, arr_v, arr_i, batt_v, batt_i);
    }
}
