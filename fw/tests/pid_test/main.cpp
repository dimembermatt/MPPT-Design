/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter PID test. Verify that:
 *  1. Liveliness - verify that the converter settles to a fixed boost ratio
 *     when hooked up to a source and a load. 
 *  2. Stability - verify that the converter can accept input and output voltage
 *     noise of a known frequency and amplitude profile and remain stable
 *     according to requirements. 
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
 *  - A0  | PA0  | ARR CURRENT
 *  - A1  | PA1  | ARR VOLTAGE
 *  - A5  | PA6  | BATT VOLTAGE
 *  - A6  | PA7  | BATT CURRENT
 *  - A3  | PA4  | PWM ENABLE
 *  - A4  | PA5  | PWM OUT
 * @note To load FastPWM: import http://os.mbed.com/users/Sissors/code/FastPWM/
 * @errata PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */

#include <math.h>
#include "mbed.h"
#include "FastPWM.h"
#include "./pid_controller/pid_controller.hpp"
#include "./Filter/MedianFilter.h"

// Control parameters
#define PWM_FREQ 50000.0
#define PWM_DUTY_START 0.5

#define HEARTBEAT_FREQ 1.0
#define REDLINE_FREQ 2.0
#define MEASURE_FREQ 10.0
#define PID_FREQ 0.5

#define FILTER_WIDTH 10
#define NUM_SENSORS 4

#define PID_P_COEFF 1E-5
#define PID_I_COEFF 0.0
#define PID_D_COEFF 0.0

// Test parameters
#define SINK_TARGET 80 // V
#define NOISE_ON 0 // 0 OFF, 1 ON
#define SOURCE_NOISE_AMPLITUDE 1.0 // V
#define SINK_NOISE_AMPLITUDE 1.0 // V

// Redline parameters
#define MIN_INP_VOLT 0.0
#define MAX_INP_VOLT 70.0
#define MIN_INP_CURR 0.0
#define MAX_INP_CURR 8.0
#define MIN_OUT_VOLT 80.0
#define MAX_OUT_VOLT 130.0
#define MIN_OUT_CURR 0.0
#define MAX_OUT_CURR 5.0
#define MIN_DUTY 0.1
#define MAX_DUTY 0.9

enum SensorIdx {
    SEN_IDX_ARRV = 0,
    SEN_IDX_ARRI = 1,
    SEN_IDX_BATTV = 2,
    SEN_IDX_BATTI = 3
};

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
    INP_OUT_INV=108,    // Input/Output Voltage inversion
    PWM_ULO=109,        // PWM Under lockout
    PWM_OLO=110         // PWM Over lockout
} ErrorCode;

typedef struct Sensors {
    float slope_correction[NUM_SENSORS] = { 1.03, 1.00, 1.00, 0.91 };
    float y_int_correction[NUM_SENSORS] = { 0.0, 0.0, 0.0, 0.0 };
} Sensors;

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
DigitalOut pwm_enable(A3);
FastPWM pwm_out(A2);
AnalogIn arr_voltage_sensor(A1);
AnalogIn arr_current_sensor(A0);
AnalogIn batt_voltage_sensor(A5);
AnalogIn batt_current_sensor(A6);
MedianFilter arr_voltage_filter(FILTER_WIDTH);
MedianFilter arr_current_filter(FILTER_WIDTH);
MedianFilter batt_voltage_filter(FILTER_WIDTH);
MedianFilter batt_current_filter(FILTER_WIDTH);
Sensors sensors;
PIDConfig_t pidConfig = PIDControllerInit(MAX_DUTY, MIN_DUTY, PID_P_COEFF, PID_I_COEFF, PID_D_COEFF);

Ticker ticker_heartbeat;
Ticker ticker_measure;
Ticker ticker_redlines;
Ticker ticker_pid;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call an event that
 * calls event_heartbeat and toggles the Heartbeat LED.
 */
void handler_heartbeat(void);

/**
 * @brief Interrupt triggered by a sensor ticker to call event
 * event_measure_sensors.
 */
void handler_measure_sensors(void);

/**
 * @brief Interrupt triggered by the redline ticker to call event
 * event_check_redlines.
 */
void handler_check_redlines(void);

/**
 * @brief Interrupt triggered by a pid ticker to call event_run_pid. 
 */
void handler_run_pid(void);

/**
 * @brief Event to print sensor output periodically.
 */
void event_heartbeat(void);

/**
 * @brief Event to measure the onboard sensors.
 */
void event_measure_sensors(void);

/**
 * @brief Event to verify that system isn't about to fault. Premptive stop.
 */
void event_check_redlines(void);

/**
 * @brief Event to execute the PID controller one cycle.
 */
void event_run_pid(void);

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

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. PID TEST.\n");

    arr_voltage_sensor.set_reference_voltage(3.321);
    arr_current_sensor.set_reference_voltage(3.321);
    batt_voltage_sensor.set_reference_voltage(3.321);
    batt_current_sensor.set_reference_voltage(3.321);

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / PWM_FREQ);
    pwm_out.write(1.0 - PWM_DUTY_START); // Inverted to get the correct output.
    pwm_enable = 1;

    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
    ticker_measure.attach(&handler_measure_sensors, (1.0 / MEASURE_FREQ));
    ticker_redlines.attach(&handler_check_redlines, (1.0 / REDLINE_FREQ));
    ticker_pid.attach(&handler_run_pid, (1.0 / PID_FREQ));
    queue.dispatch_forever();
}

void handler_heartbeat(void) {
    led_heartbeat = !led_heartbeat;
    queue.call(&event_heartbeat);
}

void handler_measure_sensors(void) {
    queue.call(&event_measure_sensors);
}

void handler_check_redlines(void) {
    queue.call(&event_check_redlines);
}

void handler_run_pid(void) {
    queue.call(&event_run_pid);
}

void event_heartbeat(void) {
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

void event_measure_sensors(void) {
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    // Inject voltage noise according to test requirement.
    arr_v += sin(rand()) * SOURCE_NOISE_AMPLITUDE - SOURCE_NOISE_AMPLITUDE / 2;
    batt_v += sin(rand()) * SINK_NOISE_AMPLITUDE - SINK_NOISE_AMPLITUDE / 2;

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

    _assert(arr_v_filtered >= MIN_INP_VOLT, INP_UVLO);
    _assert(arr_v_filtered <= MAX_INP_VOLT, INP_OVLO);

    _assert(arr_i_filtered >= MIN_INP_CURR, INP_UILO);
    _assert(arr_i_filtered <= MAX_INP_CURR, INP_OILO);

    _assert(batt_v_filtered >= MIN_OUT_VOLT, OUT_UVLO);
    _assert(batt_v_filtered <= MAX_OUT_VOLT, OUT_OVLO);

    _assert(batt_i_filtered >= MIN_OUT_CURR, OUT_UILO);
    _assert(batt_i_filtered <= MAX_OUT_CURR, OUT_OILO);

    _assert(arr_v_filtered < batt_v_filtered, INP_OUT_INV);

    float pwm = pwm_out;
    _assert(pwm >= MIN_DUTY, PWM_ULO);
    _assert(pwm <= MAX_DUTY, PWM_OLO);
}

void event_run_pid(void) {
    // TODO: check if direction of travel is correct.
    // Duty direction is reverse of error, so we invert the result.
    // We have a fixed input so we alter the output.
    float new_duty = PIDControllerStep(
        pidConfig, 
        (double) SINK_TARGET, 
        (double) batt_voltage_filter.getResult()
    );

    pwm_out.write(1.0 - new_duty); // Inverted to get the correct output.
}

float calibrate_arr_v(float inp) {
    return ((inp < 1.0) ? inp : 1.0) 
        * 114.021 
        * sensors.slope_correction[SEN_IDX_ARRV] 
        + sensors.y_int_correction[SEN_IDX_ARRV];
}

float calibrate_arr_i(float inp) {
    return ((inp < 1.0) ? inp : 1.0) 
        * 8.3025
        * sensors.slope_correction[SEN_IDX_ARRI] 
        + sensors.y_int_correction[SEN_IDX_ARRI];
}

float calibrate_batt_v(float inp) {
    return ((inp < 1.0) ? inp : 1.0) 
        * 169.371
        * sensors.slope_correction[SEN_IDX_BATTV] 
        + sensors.y_int_correction[SEN_IDX_BATTV];
}

float calibrate_batt_i(float inp) {
    return ((inp < 1.0) ? inp : 1.0) 
        * 8.3025
        * sensors.slope_correction[SEN_IDX_BATTI] 
        + sensors.y_int_correction[SEN_IDX_BATTI];
}

void _assert(bool condition, ErrorCode code) {
    // If we fail our condition, raise the flag, preemptive kill pwm, turn on the error LED
    if (!condition) { 
        printf("A redline (%u) has been crossed. Tracking is disabled.\n", code);
        
        // Disable tracking.
        pwm_enable = 0;
        led_error = 1;
        led_tracking = 0;
        ticker_measure.detach();
        ticker_redlines.detach();
    }
}
