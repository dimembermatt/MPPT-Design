/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com)
 * @brief Sunscatter power sensor test. Verify that:
 *      - Liveliness - verify that voltage and current measurements can be taken from each set of sensors.
 *      - Replication - verify that voltage and current measurements can be taken at various operating frequencies and determine precision metrics.
 *      - Accuracy - verify that the sensors are accurate within a known range of input and output conditions, with the appropriate calibration function.
 * @version 0.1.0
 * @date 2023-09-16
 *
 * @copyright Copyright (c) 2023
 *
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
 * 
 * @errata PWM_OUT A4 is not PWM enabled. Solder bridge to A2 (PA_3).
 */
#include "mbed.h"
#include "Filter/MedianFilter.h"

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut led_error(D3);
AnalogIn arr_voltage_sensor(A1);
AnalogIn arr_current_sensor(A0);
AnalogIn batt_voltage_sensor(A5);
AnalogIn batt_current_sensor(A6);

MedianFilter arr_voltage_filter(10);
MedianFilter arr_current_filter(10);
MedianFilter batt_voltage_filter(10);
MedianFilter batt_current_filter(10);


DigitalOut pwm_enable(A3);
PwmOut pwm_out(A2);

Ticker ticker_heartbeat;
EventQueue queue(32 * EVENTS_EVENT_SIZE);

/**
 * @brief Interrupt triggered by the heartbeat ticker to call an event to send a
 * pre-formed CAN message. 
 */
void handler_heartbeat(void);

/**
 * @brief Event to measure a sensor.
 */
void event_measure_sensor(void);

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

int main()
{
    set_time(0);
    ThisThread::sleep_for(1000ms);
    printf("Power Sensor Test\n");
    
    arr_voltage_sensor.set_reference_voltage(3.321);
    arr_current_sensor.set_reference_voltage(3.321);
    batt_voltage_sensor.set_reference_voltage(3.321);
    batt_current_sensor.set_reference_voltage(3.321);

    ticker_heartbeat.attach(&handler_heartbeat, 100ms);

    led_heartbeat = 0;
    led_tracking = 0;
    led_error = 0;

    pwm_out.period(1.0 / 100000.0); // 100 kHz

    // Force HIGH
    pwm_out.write(1.0);
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

    queue.dispatch_forever();
    while(true);
}

void handler_heartbeat(void) { 
    led_heartbeat = !led_heartbeat;
    queue.call(&event_measure_sensor);
}

void event_measure_sensor(void) {
    // Measure sensor
    time_t seconds = time(NULL);

    float arr_v = calibrate_arr_v(arr_voltage_sensor.read());
    float arr_i = calibrate_arr_i(arr_current_sensor.read());
    float batt_v = calibrate_batt_v(batt_voltage_sensor.read());
    float batt_i = calibrate_batt_i(batt_current_sensor.read());

    arr_voltage_filter.addSample(arr_v);
    arr_current_filter.addSample(arr_i);
    batt_voltage_filter.addSample(batt_v);
    batt_current_filter.addSample(batt_i);

    // CSV format for later analysis.
    printf(
        "%u,%f,%f,%f,%f\n", 
        (unsigned int) seconds, 
        arr_voltage_filter.getResult(), 
        arr_current_filter.getResult(), 
        batt_voltage_filter.getResult(), 
        batt_current_filter.getResult()
    );
}

float calibrate_arr_v(float inp) {
    if (inp < 1.0) return inp * 114.021;
    else return 114.021; 
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
    if (inp < 1.0) return inp * 8.3025;
    else return 8.3025;
}
