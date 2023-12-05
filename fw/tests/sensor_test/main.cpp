/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter sensor test. Verify that:
 *  1. Liveliness - verify that measurements can be taken from each sensor.   
 *  2. Variance - verify that the measurements taken at known test conditions
 *     remain stable with low variance according to requirements. 
 *  3. Accuracy - verify that the measurements taken at known test conditions
 *     remain accurate according to requirements. 
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
 * @errata v0.2.0 hardware - PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"
#include "FastPWM.h"
#include "Filter/MedianFilter.h"

// Control parameters
#define PWM_FREQ 50000.0 // v0.2.0
// 0.0 - Force LOW SIDE switch closed, HIGH side switch open
// 1.0 - Force HIGH SIDE switch closed, LOW side switch open
#define PWM_DUTY 0.5

#define HEARTBEAT_FREQ 1.0

#define MEASURE_FREQ 10.0
#define FILTER_WIDTH 10
#define NUM_SENSORS 4

enum SensorIdx {
    SEN_IDX_ARRV = 0,
    SEN_IDX_ARRI = 1,
    SEN_IDX_BATTV = 2,
    SEN_IDX_BATTI = 3
};

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

Ticker ticker_heartbeat;
Ticker ticker_measure;
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
 * @brief Event to print sensor output periodically.
 */
void event_heartbeat(void);

/**
 * @brief Event to measure the onboard sensors.
 */
void event_measure_sensors(void);

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

int main() {
    set_time(0);

    ThisThread::sleep_for(1000ms);
    printf("Starting up main program. Sensor TEST.\n");
    
    arr_voltage_sensor.set_reference_voltage(3.321);
    arr_current_sensor.set_reference_voltage(3.321);
    batt_voltage_sensor.set_reference_voltage(3.321);
    batt_current_sensor.set_reference_voltage(3.321);

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / PWM_FREQ);
    pwm_out.write(1.0 - PWM_DUTY); // Inverted to get the correct output.
    pwm_enable = 1;

    led_tracking = 1;

    /**
     * Testing:
     * - V_ARR: Supply 0 - 80 V to input and compare expected (multimeter) with received.
     * - V_BATT: enable off, supply 0 - 130 V to output and compare expected with received.
     * - I_ARR, I_BATT: enable on, 100% duty to short high side switch, tie output to short current. 
     *   Supply 0 - 6 A to input and compare expected (multimeter on both sides) with received.
     * Note that there is ~1.29V drop on some conditions (enable = 0, duty = 1.0). This may be an issue.
     */

    ticker_heartbeat.attach(&handler_heartbeat, (1.0 / HEARTBEAT_FREQ));
    ticker_measure.attach(&handler_measure_sensors, (1.0 / MEASURE_FREQ));
    queue.dispatch_forever();
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
    queue.call(&event_heartbeat);
}

void handler_measure_sensors(void) {
    queue.call(&event_measure_sensors);
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

    arr_voltage_filter.addSample(arr_v);
    arr_current_filter.addSample(arr_i);
    batt_voltage_filter.addSample(batt_v);
    batt_current_filter.addSample(batt_i);
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