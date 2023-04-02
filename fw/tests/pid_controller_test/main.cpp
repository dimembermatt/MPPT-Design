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
#include "FastPWM.h"
#include "./pid_controller/pid_controller.hpp"
#include "./Filter/MedianFilter.h"

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut led_error(PA_12);
DigitalOut pwm_enable(PA_3);
AnalogIn arr_voltage_sensor(PA_4);
AnalogIn arr_current_sensor(PA_5);
AnalogIn batt_voltage_sensor(PA_7);
AnalogIn batt_current_sensor(PA_6);
FastPWM pwm_out(PA_1);

Ticker ticker_heartbeat;
Ticker ticker_pwm_test;

float sensor_vals[4] = {0.0, 0.0, 0.0, 0.0};
float freq = 25000.0;
float duty = 1-0.51;
PIDConfig_t pidConfig = PIDControllerInit(1.0, -1.0, 1E-4, 1E-5, 0.0);
float target = 130.0; // 20 V for now
MedianFilter arr_voltage_filter(5);
MedianFilter batt_voltage_filter(5);

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

void sensor_function(void) {
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    arr_voltage_filter.addSample(arr_v);
    batt_voltage_filter.addSample(batt_v);

    sensor_vals[0] = arr_voltage_filter.getResult();
    sensor_vals[1] = arr_i;
    sensor_vals[2] = batt_voltage_filter.getResult();
    sensor_vals[3] = batt_i;
}

void plant_function(float duty) {
    pwm_out.write(duty);
}

void adjust_duty_cycle() {
    static bool state = true;
    if (state) {
        state = false;
        pwm_out.write(duty - 0.01);
    } else {
        state = true;
        pwm_out.write(duty + 0.01);
    }
}

int main()
{
    set_time(1679957180);
    
    printf("Hello world. PID Controller example. starting up.\n");
    
    // Start heartbeat.
    ticker_heartbeat.attach(&heartbeat, 1000ms);

    // 5 seconds for user to get ready.
    ThisThread::sleep_for(5000ms);

    // Indicate that tracking is about to begin.
    for (uint8_t i = 0; i < 7; ++i) {
        led_tracking = !led_tracking;
        ThisThread::sleep_for(1000ms);
    }

    // Set the pwm frequency to 104 kHz.
    float f = 104000.0;
    pwm_out.period_us(1.0E6 / f);
    pwm_out.write(duty);

    ticker_pwm_test.attach(&adjust_duty_cycle, 100ms);

    // Start PWM control.
    pwm_enable = 1;

    unsigned int idx = 0;
    while (true) {
        ThisThread::sleep_for(1ms);
        // Give enough time to capture some sensor values and have them stabilize
        // for (uint8_t i = 0; i < 5; ++i) {
        //     ThisThread::sleep_for(5ms);
            sensor_function();
        // }
        // time_t seconds = time(NULL);

        // CSV format for later analysis.
        printf(
            "%u, %f, %f, %f, %f, %f, %f\n", 
            (unsigned int) ++idx, 
            freq, 
            duty, 
            sensor_vals[0], 
            sensor_vals[1], 
            sensor_vals[2], 
            sensor_vals[3]
        );

        // Human readable debug.
        // printf(
        //     "Timestep:\t%u\n"
        //     "\tFreq:\t%f\n"
        //     "\tDuty:\t%f\n"
        //     "\tARRAY:\t\t%f V | %f A\n"
        //     "\tBATTERY:\t%f V | %f A\n",
        //     (unsigned int) seconds, 
        //     freq, 
        //     duty, 
        //     sensor_vals[0], 
        //     sensor_vals[1], 
        //     sensor_vals[2], 
        //     sensor_vals[3]
        // );

        // Duty direction is reverse of error, so we invert the result.
        // float change = PIDControllerStep(pidConfig, (double) target, (double) sensor_vals[2]);
        // float new_duty = duty - change;
        // if (new_duty > 0.90) {
        //     duty = 0.90;
        // } else if (new_duty < 0.10) {
        //     duty = 0.10;
        // } else {
        //     duty = new_duty;
        // }

        // plant_function(duty);


    }
}

