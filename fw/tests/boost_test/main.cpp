/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com.com)
 * @brief Autoselects the boosting duty cycle based on input and output voltage.
 * @version 0.1
 * @date 2023-04-02
 * @note For board revision v0.1.0. To load FastPWM: import http://os.mbed.com/users/Sissors/code/FastPWM/
 * @copyright Copyright (c) 2023
 *
 */

#include "mbed.h"
#include "FastPWM.h"
#include "./Filter/SmaFilter.h"
#include <cstdio>

#define F_SW 104000.0 // 104 khz switching

// Note: only read AnalogIn in one ISR ever since we aren't using mutexes.
class UnlockedAnalogIn : public AnalogIn {
public:
    UnlockedAnalogIn(PinName inp) : AnalogIn(inp) { }
    virtual void lock() { }
    virtual void unlock() { }
};

typedef enum Error { 
    OK=0,
    INP_UVL=100,
    INP_OVL=101,
    OUT_UVL=102,
    OUT_OVL=103,
    INP_OUT_INV=104,
} ErrorCode;
ErrorCode status = OK;

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut pwm_enable(PA_3);
FastPWM pwm_out(PA_1);
UnlockedAnalogIn arr_voltage_sensor(PA_4);
UnlockedAnalogIn batt_voltage_sensor(PA_7);
SmaFilter arr_voltage_filter(5);
SmaFilter batt_voltage_filter(5);

Ticker ticker_toggle_heartbeat;
Ticker ticker_read_sensor;
Ticker ticker_update_pwm;
Ticker ticker_check_redlines;

float calibrate_arr_v(float inp) {
    if (inp < 1.0) return inp * 114.0;
    else return 114.0;
}

float calibrate_batt_v(float inp) {
    if (inp < 1.0) return inp * 168.0 + 0.0393;
    else return 168.0;
}

void heartbeat(void) { led_heartbeat = !led_heartbeat; }
void read_sensor(void) {
    // Read in input and output voltage and insert into filter.
    arr_voltage_filter.addSample(calibrate_arr_v(arr_voltage_sensor.read()));
    batt_voltage_filter.addSample(calibrate_batt_v(batt_voltage_sensor.read()));
}
void update_pwm(void) {
    // Calculate new duty cycle.
    float arr_v_filtered = arr_voltage_filter.getResult();
    float batt_v_filtered = batt_voltage_filter.getResult();

    float duty = 1 - arr_v_filtered / batt_v_filtered;
    pwm_out.write(1 - duty); // inverse logic
}

void _assert(bool condition, ErrorCode code) {
    // If we fail our condition, raise the flag and let the main thread handle it.
    if (!condition) { status = code; }
}

void check_redlines(void) {
    float arr_v_filtered = arr_voltage_filter.getResult();
    float batt_v_filtered = batt_voltage_filter.getResult();

    // Our input must be in the range (1.0, 80.0).
    _assert(arr_v_filtered > 1.0, INP_UVL);
    _assert(arr_v_filtered < 70.0, INP_OVL);

    // Our output must be between (80.0, 130.0).
    _assert(batt_v_filtered > 70.0, OUT_UVL);
    _assert(batt_v_filtered < 130.0, OUT_OVL);

    // Our output must always be greater than our input.
    _assert(arr_v_filtered < batt_v_filtered, INP_OUT_INV);

}


int main() {
    set_time(1680461674);
    printf("Hello world. Boost test. starting up.\n");

    ticker_toggle_heartbeat.attach(&heartbeat, 1000ms);
    ticker_read_sensor.attach(&read_sensor, 10ms);

    ThisThread::sleep_for(1000ms);

    pwm_out.period_us(1.0E6 / F_SW);
    pwm_out.write(0.5); // Default duty of 50%.

    // Start tracking.
    led_tracking = 1;
    pwm_enable = 1;

    ThisThread::sleep_for(500ms);
    ticker_check_redlines.attach(&check_redlines, 100ms);

    // Start pwm update.
    ticker_update_pwm.attach(&update_pwm, 50ms);
    while (true) {
        ThisThread::sleep_for(100ms);
        
        printf(
            "%u\tV_IN: %f | V_OUT: %f | DUTY: %f\n", 
            time(NULL), 
            arr_voltage_filter.getResult(),
            batt_voltage_filter.getResult(),
            pwm_out.read()
        );

        if (status != OK) {
            pwm_enable = 0;
            led_tracking = 0;
            printf("A redline (%u) has been crossed. Tracking is disabled.\n", status);
            while (true) {
                ThisThread::sleep_for(1000ms);
            }
        }
    }
}

