#!/usr/bin/env python
import RPi.GPIO as GPIO 
import time 
from time import sleep
from multiprocessing import Process
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
lcd = I2cLcd(1, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

red_led = 13
green_led = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)

buzzer = 27
GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.LOW)

GPIO.setmode(GPIO.BCM)
L_TRIG = 4
L_ECHO = 14
R_TRIG = 17
R_ECHO = 18
B_TRIG = 26 
B_ECHO = 20
F_TRIG = 19
F_ECHO = 16

GPIO.setup(L_TRIG, GPIO.OUT) 
GPIO.setup(L_ECHO, GPIO.IN) 
GPIO.setup(R_TRIG, GPIO.OUT) 
GPIO.setup(R_ECHO, GPIO.IN) 
GPIO.setup(F_TRIG, GPIO.OUT) 
GPIO.setup(F_ECHO, GPIO.IN) 
GPIO.setup(B_TRIG, GPIO.OUT) 
GPIO.setup(B_ECHO, GPIO.IN) 

l_distance = 0
r_distance = 0
f_distance = 0
b_distance = 0

l_message = str("NORML")
b_message = str("NORML")
r_message = str("NORML")
f_message = str("NORML")


def l_us():
    global l_distance
    GPIO.output(L_TRIG, GPIO.LOW)
    time.sleep(2) 
    GPIO.output(L_TRIG, GPIO.HIGH) 
    time.sleep(0.00001) 
    GPIO.output(L_TRIG, GPIO.LOW) 
    while GPIO.input(L_ECHO)==0: 
      l_start_time = time.time() 
    while GPIO.input(L_ECHO)==1:
      l_Bounce_back_time = time.time() 
    l_pulse_duration = l_Bounce_back_time - l_start_time 
    l_distance = round(l_pulse_duration * 17150, 2) 
    print (f"Distance l_us: {l_distance} cm")

def r_us():
    global r_distance
    GPIO.output(R_TRIG, GPIO.LOW)
    time.sleep(2) 
    GPIO.output(R_TRIG, GPIO.HIGH) 
    time.sleep(0.00001) 
    GPIO.output(R_TRIG, GPIO.LOW) 
    while GPIO.input(R_ECHO)==0: 
      r_start_time = time.time() 
    while GPIO.input(R_ECHO)==1:
      r_Bounce_back_time = time.time() 
    r_pulse_duration = r_Bounce_back_time - r_start_time 
    r_distance = round(r_pulse_duration * 17150, 2) 
    print (f"Distance r_us: {r_distance} cm")

def f_us():
    global f_distance
    GPIO.output(F_TRIG, GPIO.LOW)
    time.sleep(2) 
    GPIO.output(F_TRIG, GPIO.HIGH) 
    time.sleep(0.00001) 
    GPIO.output(F_TRIG, GPIO.LOW) 
    while GPIO.input(F_ECHO)==0: 
      f_start_time = time.time() 
    while GPIO.input(F_ECHO)==1:
      f_Bounce_back_time = time.time() 
    f_pulse_duration = f_Bounce_back_time - f_start_time 
    f_distance = round(f_pulse_duration * 17150, 2) 
    print (f"Distance f_us: {f_distance} cm")

def b_us():
    global b_distance
    GPIO.output(B_TRIG, GPIO.LOW)
    time.sleep(2) 
    GPIO.output(B_TRIG, GPIO.HIGH) 
    time.sleep(0.00001) 
    GPIO.output(B_TRIG, GPIO.LOW) 
    while GPIO.input(B_ECHO)==0: 
      b_start_time = time.time() 
    while GPIO.input(B_ECHO)==1:
      b_Bounce_back_time = time.time() 
    b_pulse_duration = b_Bounce_back_time - b_start_time 
    b_distance = round(b_pulse_duration * 17150, 2)
    print (f"Distance b_us: {b_distance} cm")
    

def lcd_display():
    f_us()
    l_us()
    r_us()
    b_us()
    if f_distance <= 20.00:
      f_message == "ALERT"
    else:
      f_message == "NORML"
    if b_distance <= 20.00:
      b_message = "ALERT"
    else:
      b_message = "NORML"
    if l_distance <= 20.00:
      l_message = "ALERT"
    else:
      l_message = "NORML"
    if r_distance <= 20.00:
      r_message = "ALERT"
    else:
      r_message = "NORML"
      
    if (b_message == "NORML" and l_message == "NORML" and r_message == "NORML" and f_message == "NORML"):
        GPIO.output(green_led, GPIO.HIGH)
        GPIO.output(red_led, GPIO.LOW)
        GPIO.output(buzzer, GPIO.LOW)
    else:
        GPIO.output(green_led, GPIO.LOW)
        GPIO.output(red_led, GPIO.HIGH)
        GPIO.output(buzzer, GPIO.HIGH)
        
    lcd.putstr("F:"+str(f_message)+" B:"+str(b_message))
    lcd.move_to(0,1)
    lcd.putstr("L:"+str(l_message)+" R:"+str(r_message))

if __name__ == '__main__':
  try:
      while True:
          p1 = Process(target = l_us)
          p2 = Process(target = r_us)
          p3 = Process(target = f_us)
          p4 = Process(target = b_us)
          p5 = Process(target = lcd_display)
          p1.start()
          p2.start()
          p3.start()
          p4.start()
          p5.start()
          p1.join()
          p2.join()
          p3.join()
          p4.join()
          p5.join()

  except KeyboardInterrupt:
    pass
  finally:
      lcd.clear()
      GPIO.cleanup()