################################################################
# Pedestrian Lights Controller by Sen (Offline Version)
# v 0.2 (simply simplier)
# https://github.com/senwerks/pedestrian-lights
#
# TODO: Actually test this file, it's only been run in my head
################################################################

from machine import Pin
import time

# Timer Period - Edit this to change "Green" time.
timer_period = 180 # Set to 180 when Live

# Set up the 2 relay pins
green_light = Pin(27, Pin.OUT)
green_light.value(0)
red_light = Pin(28, Pin.OUT)
red_light.value(0)

# Set up the physical button
pin = Pin(22, Pin.IN, Pin.PULL_UP)

# Button interrupt and debounce
interrupt_flag = 0
debounce_time = 0

# Ghetto State Machine
state = "Off"
states = ["Go", "Flash", "Stop", "Timer", "Boot"]

def change_state(state):
    print('Changed to %s State' % state)
    global green_light, red_light
    
    if state == "Go":
        green_light.value(1)
        red_light.value(0)
    elif state == "Flash":
        green_light.value(0)
        for i in range(10):
            red_light.value(1)
            time.sleep(0.5)
            red_light.value(0)
            time.sleep(0.5)
        change_state("Stop")
    elif state == "Stop":
        green_light.value(0)
        red_light.value(1)
    elif state == "Timer":
        green_light.value(1)
        red_light.value(0)
        time.sleep(timer_period)
        change_state("Flash")
    elif state == "Boot":
        for i in range(5):
            red_light.value(1)
            green_light.value(1)
            time.sleep(0.2)
            red_light.value(0)
            green_light.value(0)
            time.sleep(0.2)
        change_state("Stop")
    
def callback(pin):
    global interrupt_flag, debounce_time
    if (time.ticks_ms() - debounce_time) > 500:
        interrupt_flag = 1
        debounce_time = time.ticks_ms()

pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Time to put it all together...
change_state("Boot")

while True:
    if interrupt_flag == 1:
        interrupt_flag = 0
        print("Button Pressed!")
        change_state("Timer")
        # or rotate through available States:
        # state = states[(states.index(state) + 1) % len(states)]
        #change_state(state)
    time.sleep(0.1)  # Add a small delay to avoid high CPU usage

