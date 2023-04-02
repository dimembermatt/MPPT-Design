/**
 * @file main.cpp
 * @author Matthew Yu (matthewjkyu@gmail.com.com)
 * @brief Tests the PWM gate driver. Two modes, one for feedback using BNC, the
 *        other uses manual control.
 * @version 0.1
 * @date 2023-03-26
 * @note For board revision v0.1.0. To load FastPWM: import http://os.mbed.com/users/Sissors/code/FastPWM/
 * @copyright Copyright (c) 2023
 *
 */

#include "mbed.h"
#include "FastPWM.h"

// Switching frequency is 104kHz.
// Duty cycle is a function of pwm_control, which takes a value from 0 - 1 V.


#define __MODE__ 1 // 0 for using BNC, 1 if manual control

#if __MODE__ == 0
DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut pwm_enable(PA_3);
AnalogIn pwm_control(PA_0);
FastPWM pwm_out(PA_1);

Ticker ticker_heartbeat;
Ticker ticker_pwm_update;


void heartbeat() { led_heartbeat = !led_heartbeat; }
void adjust_duty_cycle() {
    float inp = pwm_control.read();
    pwm_out.write(inp);
}

int main()
{
    // Set the pwm frequency to 104 kHz.
    float f = 100000.0;
    pwm_out.period_us(1.0E6 / f);

    // Indicate that pwm is running.
    led_tracking = 1;

    // Start heartbeat.
    ticker_heartbeat.attach(&heartbeat, 1000ms);

    // Start PWM control.
    pwm_enable = 1;
    ticker_pwm_update.attach(&adjust_duty_cycle, 100ms);

    while (true) {
        ThisThread::sleep_for(1000ms);
        printf("MODE 0.\n");
    }
}

#else
DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut pwm_enable(PA_3);
FastPWM pwm_out(PA_1);

Ticker ticker_heartbeat;
Ticker ticker_pwm_update;

void heartbeat() { led_heartbeat = !led_heartbeat; }
void adjust_duty_cycle() {
    // static int inp = 0.0;
    // static float n = 1;
    // inp = (inp + 1) % 101;
    // pwm_out.write((float) inp / 1000.00);
    // n *= 1.05;
    // if (n > 10000000) { n = 1; }
    // pwm_out.period(1.0/n);

}

int main()
{
    // Set the pwm frequency to 104 kHz.
    printf("HELLO WORLD\n");
    float f = 100000.0;
    float d = 1-0.776;
    pwm_out.period_us(1.0E6 / f);
    pwm_out.write(d);

    // Indicate that pwm is running.
    led_tracking = 1;

    // Start heartbeat.
    ticker_heartbeat.attach(&heartbeat, 100ms);

    // Start PWM control.
    pwm_enable = 1;
    ticker_pwm_update.attach(&adjust_duty_cycle, 00ms);

    // V = IR
    // I = V/R
    // P = V^2 / R
    // sqrt(P * R)
    // 44.7V output, 1.12 A 50 W
    // 10 V input, 5 A

    7 A, 10V input
    1.5 A, 41.95 V output
    70 W inp, 63 W out

    while (true) {
        ThisThread::sleep_for(0ms);
        // d += 0.01;
        // if (d > 1.0) { d = 0.0;}
        // // printf("FREQ: %i\tDUTY: %i.\n", ((int)(f*100)), ((int)(d*1000)));
        // pwm_out.write(d);
    }
}

#endif