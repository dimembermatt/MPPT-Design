#include "DigitalOut.h"
#include "ThisThread.h"
#include "mbed.h"
#include <cstdio>

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut led_error(PA_12);

AnalogIn arr_voltage_sensor(PA_4);
AnalogIn arr_current_sensor(PA_5);
AnalogIn batt_voltage_sensor(PA_7);
AnalogIn batt_current_sensor(PA_6);

// AnalogIn pwm_control(PA_0);
// DigitalOut pwm_enable(PA_3);
// PwmOut pwm_out(PA_0); // Not PWM pin

Ticker ticker_heartbeat;
void heartbeat(){ led_heartbeat = !led_heartbeat; }

int main()
{
    ticker_heartbeat.attach(&heartbeat, 1000ms);

    while (true) {
        ThisThread::sleep_for(1000);
    }
}

