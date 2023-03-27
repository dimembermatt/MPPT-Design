/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Performs basic PID controller loop for fixed output given some input
 *        lower than the output.
 * @version 0.1
 * @date 2023-03-26
 * @note For board revision v0.1.0.
 * @copyright Copyright (c) 2023
 *
 */

#include "mbed.h"
#include "./pid_controller/pid_controller.hpp"

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut led_error(PA_12);
DigitalOut pwm_enable(PA_3);
AnalogIn arr_voltage_sensor(PA_4);
AnalogIn arr_current_sensor(PA_5);
AnalogIn batt_voltage_sensor(PA_7);
AnalogIn batt_current_sensor(PA_6);
PwmOut pwm_out(PA_1);

Ticker ticker_heartbeat;
Ticker ticker_measure_adcs;
Ticker ticker_pwm_update;

static float sensor_vals[4] = {0.0, 0.0, 0.0, 0.0};
static float freq = 104000.0;
static float duty = 1.0;
static PIDConfig_t pidConfig = PIDControllerInit(1.0, 0.0, 0.01, 0.0, 0.0);
static float target = 20.0; // 20 V for now

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

void sensor_function(void) {
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    sensor_vals[0] = arr_v;
    sensor_vals[1] = arr_i;
    sensor_vals[2] = batt_v;
    sensor_vals[3] = batt_i;
}

void plant_function(float duty) {
    pwm_out.write(duty);
}

int main()
{
    // Start heartbeat.
    ticker_heartbeat.attach(&heartbeat, 1000ms);

    // Set the pwm frequency to 104 kHz.
    pwm_out.period(1.0/104000.0);

    // Indicate that pwm is running.
    led_tracking = 1;

    // Start PWM control.
    pwm_enable = 1;

    while (true) {
        ThisThread::sleep_for(1000ms);
        sensor_function();
        printf("ARR: %f V, %f A\n", sensor_vals[0], sensor_vals[1]);
        printf("BATT: %f V, %f A\n", sensor_vals[2], sensor_vals[3]);
        printf("PWM: %f Hz, %f pct\n", freq, duty);

        plant_function(PIDControllerStep(pidConfig, (double) target, (double) sensor_vals[2]));
    }
}

