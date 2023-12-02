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

#include "ThisThread.h"
#include "mbed.h"
#include "FastPWM.h"
#include <chrono>
using namespace std::chrono;


// Switching frequency is 104kHz.
// Duty cycle is a function of pwm_control, which takes a value from 0 - 1 V.


#define __MODE__ 1 // 0 for using BNC, 1 if manual control

#if __MODE__ == 0
class UnlockedAnalogIn : public AnalogIn {
public:
    UnlockedAnalogIn(PinName inp) : AnalogIn(inp) { }
    virtual void lock() { }
    virtual void unlock() { }
};

DigitalOut led_heartbeat(PA_9);
DigitalOut led_tracking(PA_10);
DigitalOut pwm_enable(PA_3);
UnlockedAnalogIn pwm_control(PA_0);
FastPWM pwm_out(PA_1);

Ticker ticker_heartbeat;
Timer t;


void heartbeat() { led_heartbeat = !led_heartbeat; }
inline void adjust_duty_cycle() {
    pwm_out.write(pwm_control.read());
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

    printf("HELLO WORLD MOKUGO MODE\n");
    // Start PWM control.
    pwm_enable = 1;

    while (true) {
        // 22 uS, max update freq is ~45kHz
        // uint32_t i;
        // t.reset();
        // t.start();
        // for (i = 0; ++i < 100000;) {
            adjust_duty_cycle();
        // }
        // t.stop();
        // printf("The time taken was %llu microseconds\n", duration_cast<microseconds>(t.elapsed_time()/100000).count());
    }
}


#else

DigitalOut led_heartbeat(D1);
DigitalOut led_tracking(D0);
DigitalOut pwm_enable(A3);
FastPWM pwm_out(A2);

Ticker ticker_heartbeat;
Ticker ticker_pwm_update;

void heartbeat() { led_heartbeat = !led_heartbeat; }
void adjust_duty_cycle() {
    static int inp = 0.0;
    static float n = 1;
    inp = (inp + 1) % 101;
    pwm_out.write((float) inp / 100.00);
}

int main()
{
    ThisThread::sleep_for(500ms);

    // Set the pwm frequency to 100 kHz.
    printf("HELLO WORLD FIXED MODE\n");
    float f = 100000.0;
    float d = 1-0.5;
    pwm_out.period_us(1.0E6 / f);
    pwm_out.write(d);

    // Indicate that pwm is running.
    led_tracking = 1;

    // Start heartbeat.
    ticker_heartbeat.attach(&heartbeat, 500ms);

    // Start PWM control.
    pwm_enable = 1;
    // ticker_pwm_update.attach(&adjust_duty_cycle, 100ms);

    while (true) {
        ThisThread::sleep_for(1000ms);
    }
}

#endif