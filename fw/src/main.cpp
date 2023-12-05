/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Main program for Sunscatter. Measures voltage and current for the
 * solar array and battery and performs appropriate boosting function.
 * Documentation at SYSTEM_DESIGN.md.
 * @version 0.2.0
 * @date 2023-12-02
 * @copyright Copyright (c) 2023
 *
 * @note For board revision v0.2.0.
 * @note Pinout:
 *  - D1  | PA9  | HEARTBEAT LED
 *  - D0  | PA10 | TRACKING LED
 *  - D3  | PB0  | ERROR LED
 * 
 *  - D2  | PA12 | CAN_TX
 *  - D10 | PA11 | CAN_RX
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

#include "mbed.h"
#include "FastPWM.h"
#include "./pid_controller/pid_controller.hpp"
#include "./Filter/MedianFilter.h"

// Debug define
#define __DEBUG__ 1 // 0 - no debug, 1 - turn on DEBUG, auto start and disable CAN

// Control parameters
#define PWM_FREQ 50000.0
#define PWM_DUTY_START 0.5

#define HEARTBEAT_FREQ 1.0
#define REDLINE_FREQ 2.0
#define MEASURE_FREQ 10.0
#define PID_FREQ 2.0
#define MPPT_FREQ 0.25

#define FILTER_WIDTH 10
#define NUM_SENSORS 4

#define PID_P_COEFF 1E-5
#define PID_I_COEFF 0.0
#define PID_D_COEFF 0.0

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

// CAN IDs
#define BOARD_CAN_MODIFIER 0x000 // A - 0x000, B - 0x010, C - 0x020
#define CAN_HEARTBEAT   0x600
#define CAN_SET_MODE    0x601
#define CAN_SS_FAULT    0x602
#define CAN_ACK_FAULT   0x603
#define CAN_SEN_CONF1   0x604
#define CAN_SEN_CONF2   0x605
#define CAN_SEN_CONF3   0x606
#define CAN_CON_CONF    0x607
#define CAN_DEB_CONF    0x608
#define CAN_OP_SET      0x609
#define CAN_ARRV_MEA    0x60A
#define CAN_ARRI_MEA    0x60B
#define CAN_BATTV_MEA   0x60C
#define CAN_BATTI_MEA   0x60D

enum State {
    STATE_STOP = 0,
    STATE_RUN = 1,
    STATE_ERROR = 2
};

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
CAN can(D10, D2);
Sensors sensors;
PIDConfig_t pidConfig = PIDControllerInit(MAX_DUTY, MIN_DUTY, PID_P_COEFF, PID_I_COEFF, PID_D_COEFF);

Ticker ticker_heartbeat;
Ticker ticker_measure;
Ticker ticker_redlines;
Ticker ticker_pid;
Ticker ticker_mppt;
EventQueue queue(32 * EVENTS_EVENT_SIZE);


ErrorCode status = OK;
enum State current_state;
bool is_error;
bool set_mode;
bool ack_fault;
double ref_inp_v;

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
 * @brief Interrupt triggered by a mppt ticker to call event_run_mppt. 
 */
void handler_run_mppt(void);

/**
 * @brief Interrupt triggered by a CAN RX IRQ to call event
 * event_process_can.
 */
void handler_process_can(void);

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
 * @brief Event to execute the MPPT algorithm one cycle.
 */
void event_run_mppt(void);

/**
 * @brief Event to process incoming CAN messages.
 */
void event_process_can(void);

/**
 * @brief Event to update the state machine and manage any tickers.
 */
void event_update_state_machine(void);

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

int main(void) {
    set_time(0);

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. MPPT SRC.\n");

    arr_voltage_sensor.set_reference_voltage(3.321);
    arr_current_sensor.set_reference_voltage(3.321);
    batt_voltage_sensor.set_reference_voltage(3.321);
    batt_current_sensor.set_reference_voltage(3.321);

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;
    is_error = false;
    set_mode = false;
    ack_fault = false;
    current_state = STATE_STOP;
    ref_inp_v = 0.0; // TODO: double check starting point, maybe should be VOC

    pwm_enable = 0;
    pwm_out.period(1.0 / PWM_FREQ);

    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
    ticker_measure.attach(&handler_measure_sensors, (1.0 / MEASURE_FREQ));
    ticker_redlines.attach(&handler_check_redlines, (1.0 / REDLINE_FREQ));
    ticker_pid.attach(&handler_run_pid, (1.0 / PID_FREQ));
    ticker_mppt.attach(&handler_run_mppt, (1.0 / MPPT_FREQ));
    can.attach(&handler_process_can, CAN::RxIrq);

#if __DEBUG__ == 1
    // Force state machine on.
    set_mode = true;
    queue.call(&event_update_state_machine);
#endif

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

void handler_run_mppt(void) {
    queue.call(&event_run_mppt);
}

void handler_process_can(void) {
    queue.call(&event_process_can);
}

void event_heartbeat(void) {
#if __DEBUG__ == 1
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
#else
    char counter = seconds;
    CANMessage message(CAN_HEARTBEAT, &counter, 1);
    can.write(message);
#endif
}

void event_measure_sensors(void) {
    // Measure sensors
    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    // Update filters
    arr_voltage_filter.addSample(arr_v);
    arr_current_filter.addSample(arr_i);
    batt_voltage_filter.addSample(batt_v);
    batt_current_filter.addSample(batt_i);

#if __DEBUG__ == 0
    // Get results
    float arr_v_filtered = arr_voltage_filter.getResult();
    float arr_i_filtered = arr_current_filter.getResult();
    float batt_v_filtered = batt_voltage_filter.getResult();
    float batt_i_filtered = batt_current_filter.getResult();

    // Output on CAN
    can.write(CANMessage(CAN_ARRV_MEA, (uint8_t*)&arr_v_filtered, 4));
    can.write(CANMessage(CAN_ARRI_MEA, (uint8_t*)&arr_i_filtered, 4));
    can.write(CANMessage(CAN_BATTV_MEA, (uint8_t*)&batt_v_filtered, 4));
    can.write(CANMessage(CAN_BATTI_MEA, (uint8_t*)&batt_i_filtered, 4));
#endif
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

double target_source_voltage = 0.0;

void event_run_pid(void) {
    // Duty direction is reverse of error, so we invert the result.
    float new_duty = PIDControllerStep(
        pidConfig, 
        (double) ref_inp_v, 
        (double) arr_voltage_filter.getResult()
    );

    pwm_out.write(1.0 - new_duty); // Inverted to get the correct output.
}

float prev_arr_v = 0.0;
float prev_arr_p = 0.0;
void event_run_mppt(void) {    
    // Step through MPPT once

    // Primitive PandO taken from https://github.com/lhr-solar/MPPT/blob/master/mppt/PandO.h

    // Get sensor data
    float arr_v = arr_voltage_filter.getResult();
    float arr_i = arr_current_filter.getResult();
    float batt_v = batt_voltage_filter.getResult();
    float batt_i = batt_current_filter.getResult();

    // run the algorithm
    // generate the differences
    float delta_arr_v = arr_v - prev_arr_v;
    float delta_arr_p = arr_v * arr_i - prev_arr_p;

    // get the voltage perturb stride (pwm) 
    float stride = 0.1;

    // determine the direction of movement and vref
    ref_inp_v = arr_v;
    if (delta_arr_p >= 0.0) {
        if (delta_arr_v > 0.0) {
            // Increase ref pwm
            ref_inp_v += stride;
        } else {
            // Decrease ref pwm
            ref_inp_v -= stride;
        }
    } else {
        if (delta_arr_v >= 0.0) {
            // Decrease ref pwm
            ref_inp_v -= stride;
        } else {
            // Increase ref pwm
            ref_inp_v += stride;
        }
    }

    // Derive and set reference pwm starting point
    float ref_pwm = 1.0 - (ref_inp_v / batt_v);
    pwm_out.write(1.0 - ref_pwm); // Negative logic duty cycle

    printf("\t\t\t\t\t%f, %f, %f, %f\n", delta_arr_v, delta_arr_p, ref_inp_v, ref_pwm);

    // assign old variables
    prev_arr_v = arr_v;
    prev_arr_p = arr_v * arr_i;
}

void event_process_can(void) {
    // TODO: Read message
    uint32_t can_id = 0;
    switch (can_id) {
        case CAN_SET_MODE:
            // TODO: change state machine mode.
            set_mode = false;
            queue.call(&event_update_state_machine);
            break;
        case CAN_ACK_FAULT:
            // TODO: ack fault and exit error state.
            ack_fault = true;
            queue.call(&event_update_state_machine);
            break;
        case CAN_SEN_CONF1:
        case CAN_SEN_CONF2:
        case CAN_SEN_CONF3:
        case CAN_CON_CONF:
        case CAN_DEB_CONF:
            // TODO: Not implemented. Throw exception.
            break;
        default:
            // Ignore any other CAN messages.
            break;
    }
}

void event_update_state_machine(void) {
    switch (current_state) {
        case STATE_STOP:
            // Check if CAN SET_MODE is RUN
            if (set_mode) current_state = STATE_RUN;
            // Check if error occurred
            if (is_error) current_state = STATE_ERROR;
            break;
        case STATE_RUN:
            // Check if CAN SET_MODE is STOP
            if (!set_mode) current_state = STATE_STOP;
            // Check if error occurred
            if (is_error)  current_state = STATE_ERROR;
            break;
        case STATE_ERROR:
            if (ack_fault) {
                // Acknowledge fault and jump back to STOP.
                is_error = false;
                ack_fault = false;
                set_mode = false;
                current_state = STATE_STOP;
            }
            break;
    }

    printf("Current state: %u\n", current_state);

    switch (current_state) {
        case STATE_STOP:
            // Turn off tracking LED
            // Turn off error LED
            // Disable and reset MPPT controller
            pwm_enable = 0;
            pwm_out.write(1.0 - 0.5); // 50% duty cycle.
            ticker_mppt.detach();
            prev_arr_v = 0.0;
            prev_arr_p = 0.0;

            led_tracking = 0;
            led_error = 0;
            break;
        case STATE_RUN:
            // Turn on tracking LED
            // Turn off error LED
            // Enable MPPT controller
            ticker_mppt.attach(handler_run_mppt, (1.0 / MPPT_FREQ));
            pwm_enable = 1;

            led_tracking = 1;
            led_error = 0;
            break;
        case STATE_ERROR:
            // Turn on error LED
            // Turn off tracking LED
            // Disable and reset MPPT controller
            pwm_enable = 0;
            pwm_out.write(1.0 - 0.5); // 50% duty cycle.
            ticker_mppt.detach();
            prev_arr_v = 0.0;
            prev_arr_p = 0.0;

            led_error = 1;
            led_tracking = 0;
            break;
    }
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
    // If we fail our condition, raise the flag, preemptive kill pwm, and let the main thread handle it.
    if (!condition) { 
        // Disable tracking - quick!.
        pwm_enable = 0;

#if __DEBUG__ == 1
        printf("A redline (%u) has been crossed. Tracking is disabled.\n", code);
#else
        uint16_t error = code;
        can.write(CANMessage(CAN_SS_FAULT, (uint8_t*)&error, 2));
#endif

        // Update state machine.
        is_error = true;
        queue.call(&event_update_state_machine);
    }
}