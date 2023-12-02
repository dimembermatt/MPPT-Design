/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com.com)
 * @brief Boosts at a fixed duty cycle to test steady state perfomance.
 * @version 0.1
 * @date 2023-04-02
 * @note For board revision v0.1.0. To load FastPWM: import http://os.mbed.com/users/Sissors/code/FastPWM/
 * @copyright Copyright (c) 2023
 *
 */

#include "MedianFilter.h"
#include "ThisThread.h"
#include "mbed.h"
#include "FastPWM.h"
#include "./Filter/SmaFilter.h"
#include <cstdio>

#define PWM_FREQ 100000.0
#define DUTY_CYCLE 0.75

typedef enum Error { 
    OK=0,
    INP_UVLO=100,       // Input Undervoltage lockout
    INP_OVLO=101,       // Input Overvoltage lockout
    INP_UILO=102,       // Input Undercurrent lockout
    INP_OILO=103,       // Input Overcurrent lockout
    OUT_UVLO=104,       // Output Undervoltage lockout
    OUT_OVLO=105,       // Output Overvoltage lockout
    OUT_UILO=106,       // Output Undercurrent lockout
    OUT_OILO=107,       // Output Overcurrent lockout
    INP_OUT_INV=108,    // Input/Output Voltage version
} ErrorCode;
ErrorCode status = OK;

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
AnalogIn arr_voltage_sensor(A1);
AnalogIn arr_current_sensor(A0);
AnalogIn batt_voltage_sensor(A5);
AnalogIn batt_current_sensor(A6);

MedianFilter arr_voltage_filter(30);
MedianFilter arr_current_filter(30);
MedianFilter batt_voltage_filter(30);
MedianFilter batt_current_filter(30);

DigitalOut pwm_enable(A3);
FastPWM pwm_out(A2);

Ticker ticker_heartbeat;
Ticker ticker_measure;
Ticker ticker_redlines;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call an event that
 * toggles the Heartbeat LED and prints the sensors.
 */
void handler_heartbeat(void);

/**
 * @brief Interrupt triggered by the measure ticker to call an event that 
 * updates the sensors.
 */
void handler_measure(void);

/**
 * @brief Interrupt triggered by the redline ticker to call an event to 
 * check if redlines are valid.
 */
void handler_redlines(void);

/**
 * @brief Event to print sensor output periodically.
 */
void event_heartbeat(void);

/**
 * @brief Event to measure a sensor.
 */
void event_measure_sensor(void);

/**
 * @brief Event to verify that system isn't about to fault. Premptive stop.
 */
void event_check_redlines(void);

/**
 * @brief Apply calibration function for the array voltage sensor.
 * 
 * @param inp Input value of ADC 0.0 - 1.0.
 * @return float Voltage, Volts.
 */
float calibrate_arr_v(float inp);

/**
 * @brief Apply calibration function for the array current sensor.
 * 
 * @param inp Input value of ADC 0.0 - 1.0.
 * @return float Voltage, Volts.
 */
float calibrate_arr_i(float inp);

/**
 * @brief Apply calibration function for the battery voltage sensor.
 * 
 * @param inp Input value of ADC 0.0 - 1.0.
 * @return float Voltage, Volts.
 */
float calibrate_batt_v(float inp);

/**
 * @brief Apply calibration function for the battery current sensor.
 * 
 * @param inp Input value of ADC 0.0 - 1.0.
 * @return float Voltage, Volts.
 */
float calibrate_batt_i(float inp);

/**
 * @brief Realtime assert check on a specific condition.
 * 
 * @param condition Condition to evaluate.
 * @param code Error code associated with assert failure.
 */
void _assert(bool condition, ErrorCode code);

int main() {
    set_time(0);
    printf("Hello world. Boost test. starting up.\n");

    arr_voltage_sensor.set_reference_voltage(3.321);
    arr_current_sensor.set_reference_voltage(3.321);
    batt_voltage_sensor.set_reference_voltage(3.321);
    batt_current_sensor.set_reference_voltage(3.321);

    ticker_heartbeat.attach(&handler_heartbeat, 1000ms);
    ticker_measure.attach(&handler_measure, 100ms);

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / PWM_FREQ); // 100 kHz

    // 50% duty cycle.
    pwm_out.write(1.0 - DUTY_CYCLE);
    pwm_enable = 1;

    led_tracking = 1;

    // ticker_redlines.attach(&handler_redlines, 1000ms);

    printf("Operating freq: %f\n", PWM_FREQ);
    printf("Operating duty cycle: %f\n", DUTY_CYCLE);

    queue.dispatch_forever();
    while(true);
}

void handler_heartbeat(void) { 
    queue.call(&event_heartbeat);
}

void handler_measure(void) {
    queue.call(&event_measure_sensor);
}

void handler_redlines(void) {
    queue.call(&event_check_redlines);
}

void event_heartbeat(void) {
    led_heartbeat = !led_heartbeat;
    // CSV format for later analysis.
    time_t seconds = time(NULL);
    printf(
        "%u,%f,%f,%f,%f\n", 
        (unsigned int) seconds, 
        arr_voltage_filter.getResult(), 
        arr_current_filter.getResult(), 
        batt_voltage_filter.getResult(), 
        batt_current_filter.getResult()
    );
}

void event_measure_sensor(void) {
    // Measure sensor
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    arr_voltage_filter.addSample(arr_v);
    arr_current_filter.addSample(arr_i);
    batt_voltage_filter.addSample(batt_v);
    batt_current_filter.addSample(batt_i);
}

void event_check_redlines(void) {
    float arr_v_filtered = arr_voltage_filter.getResult();
    float arr_i_filtered = arr_current_filter.getResult();
    float batt_v_filtered = batt_voltage_filter.getResult();
    float batt_i_filtered = batt_current_filter.getResult();

    // Our input voltage must be in the range [1.0, 70.0].
    _assert(arr_v_filtered >= 1.0, INP_UVLO);
    _assert(arr_v_filtered <= 70.0, INP_OVLO);

    // Our input current must be in the range [0.0 - 8.0].
    _assert(arr_i_filtered >= 0.0, INP_UILO);
    _assert(arr_i_filtered <= 8.0, INP_OILO);

    // Our output voltage must be between [80.0, 130.0].
    _assert(batt_v_filtered >= 80.0, OUT_UVLO);
    _assert(batt_v_filtered <= 130.0, OUT_OVLO);

    // Our output current must be in the range [0.0 - 5.0].
    _assert(batt_i_filtered >= 0.0, OUT_UILO);
    _assert(batt_i_filtered <= 5.0, OUT_OILO);

    // Our output must always be greater than our input.
    _assert(arr_v_filtered < batt_v_filtered, INP_OUT_INV);
}

float calibrate_arr_v(float inp) {
    if (inp < 1.0) return inp * 114.021 * 1.03;
    else return 114.021 * 1.03; 
}

float calibrate_arr_i(float inp) {
    if (inp < 1.0) return inp * 8.3025;
    else return 8.3025;
}

float calibrate_batt_v(float inp) {
    if (inp < 1.0) return inp * 169.371;
    else return 169.371;
}

float calibrate_batt_i(float inp) {
    if (inp < 1.0) return inp * 8.3025 * 0.91;
    else return 8.3025 * 0.91;
}

void _assert(bool condition, ErrorCode code) {
    // If we fail our condition, raise the flag and let the main thread handle it.
    if (!condition) { 
        printf("A redline (%u) has been crossed. Tracking is disabled.\n", code);
        
        // Disable tracking.
        pwm_enable = 0;
        led_tracking = 0;
    }
}