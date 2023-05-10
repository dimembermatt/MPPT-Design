/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Performs basic PID controller loop for fixed output given some input
 *        lower than the output.
 * @version 0.1
 * @date 2023-04-02
 * @note For board revision v0.1.0.
 * @copyright Copyright (c) 2023
 *
 */

#include <math.h>
#include "mbed.h"
#include "FastPWM.h"
#include "./pid_controller/pid_controller.hpp"
#include "./Filter/SmaFilter.h"

#define F_SW 104000.0 // 104 khz switching
#define TARGET 86.0

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

PIDConfig_t pidConfig = PIDControllerInit(0.9, -0.9, 5E-4, 3E-6, 0.0);

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut led_error(PA_12);
DigitalOut pwm_enable(PA_3);
FastPWM pwm_out(PA_1);
UnlockedAnalogIn arr_voltage_sensor(PA_4);
UnlockedAnalogIn arr_current_sensor(PA_5);
UnlockedAnalogIn batt_voltage_sensor(PA_7);
UnlockedAnalogIn batt_current_sensor(PA_6);
SmaFilter arr_voltage_filter(1);
SmaFilter batt_voltage_filter(1);
SmaFilter arr_current_filter(1);
SmaFilter batt_current_filter(1);

Ticker ticker_toggle_heartbeat;
Ticker ticker_read_sensor;
Ticker ticker_update_pwm;
Ticker ticker_check_redlines;

static int x = 0;

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

void read_sensor(void) {
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    // INJECT NOISE :O
    float amplitude = TARGET * 0.001;
    float noise = sin(3.14/100 * (++x)) * amplitude;
    batt_v += noise;

    arr_voltage_filter.addSample(arr_v);
    arr_current_filter.addSample(arr_i);
    batt_voltage_filter.addSample(batt_v);
    batt_current_filter.addSample(batt_i);
}
void run_pid_controller(void) {
    // Duty direction is reverse of error, so we invert the result.
    float change = PIDControllerStep(pidConfig, (double) TARGET, (double) batt_voltage_filter.getResult());
    float duty = pwm_out.read();
    float new_duty = duty - change;
    if (new_duty > 0.90) {
        duty = 0.90;
    } else if (new_duty < 0.10) {
        duty = 0.10;
    } else {
        duty = new_duty;
    }

    pwm_out.write(duty);
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

#define CYCLE_PERIOD 5ms
int main()
{
    set_time(1680461674);
    
    printf("Hello world. PID Controller example. starting up.\n");
    
    // Start heartbeat.
    ticker_toggle_heartbeat.attach(&heartbeat, 1000ms);
    ticker_read_sensor.attach(&read_sensor, CYCLE_PERIOD);

    // 5 seconds for user to get ready.
    ThisThread::sleep_for(5000ms);

    // Set the pwm frequency to 104 kHz.
    pwm_out.period_us(1.0E6 / F_SW);
    pwm_out.write(0.10); // Default duty cycle of 50%.

    // Start tracking.
    led_tracking = 1;
    pwm_enable = 1;

    ThisThread::sleep_for(500ms);
    ticker_check_redlines.attach(&check_redlines, 10ms);

    // Start pwm update.
    ticker_update_pwm.attach(&run_pid_controller, CYCLE_PERIOD);
    while (true) {
        ThisThread::sleep_for(CYCLE_PERIOD);
        // CSV format for later analysis.
        float amplitude = TARGET * 0.001;
        float noise = sin(3.14/100 * (x)) * amplitude;
        printf(
            "%u, %f, %f, %f, %f, %f, %f\n", 
            time(NULL), 
            arr_voltage_filter.getResult(),
            arr_current_filter.getResult(),
            batt_voltage_filter.getResult(),
            batt_current_filter.getResult(),
            pwm_out.read(),
            noise
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

