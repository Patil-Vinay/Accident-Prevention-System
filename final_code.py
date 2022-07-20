#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# alert when something is closer than this (in cm)
ALERT_DISTANCE = 20

red_led = 13
green_led = 21
buzzer = 27

# trig and echo pin for each side
sensors = {
    "F": (19, 16),
    "B": (26, 20),
    "L": (4, 14),
    "R": (17, 18),
}

GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

for trig, echo in sensors.values():
    GPIO.setup(trig, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(echo, GPIO.IN)


def get_distance(trig, echo):
    # 10us pulse on trig starts one reading
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig, GPIO.LOW)

    # return None if there is no echo in time, so the loop does not get stuck
    timeout = time.time() + 0.1
    start_time = time.time()
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if start_time > timeout:
            return None
    bounce_back_time = time.time()
    while GPIO.input(echo) == 1:
        bounce_back_time = time.time()
        if bounce_back_time > timeout:
            return None

    pulse_duration = bounce_back_time - start_time
    return round(pulse_duration * 17150, 2)


def check_sides():
    messages = {}
    # read one sensor at a time, otherwise they pick up each other's echo
    for side, (trig, echo) in sensors.items():
        distance = get_distance(trig, echo)
        if distance is None:
            print(f"Distance {side}: no echo")
        else:
            print(f"Distance {side}: {distance} cm")

        if distance is not None and distance <= ALERT_DISTANCE:
            messages[side] = "ALERT"
        else:
            messages[side] = "NORML"
        time.sleep(0.06)
    return messages


def update_outputs(messages):
    if "ALERT" in messages.values():
        GPIO.output(green_led, GPIO.LOW)
        GPIO.output(red_led, GPIO.HIGH)
        GPIO.output(buzzer, GPIO.HIGH)
    else:
        GPIO.output(green_led, GPIO.HIGH)
        GPIO.output(red_led, GPIO.LOW)
        GPIO.output(buzzer, GPIO.LOW)

    lcd.move_to(0, 0)
    lcd.putstr("F:" + messages["F"] + " B:" + messages["B"])
    lcd.move_to(0, 1)
    lcd.putstr("L:" + messages["L"] + " R:" + messages["R"])


if __name__ == '__main__':
    try:
        # let the sensors settle before the first reading
        time.sleep(2)
        while True:
            update_outputs(check_sides())

    except KeyboardInterrupt:
        pass
    finally:
        lcd.clear()
        GPIO.cleanup()
