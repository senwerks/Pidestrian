################################################################
# Pedestrian Lights Controller by Sen (Offline Version)
# v 0.1 (simply simple)
# https://github.com/senwerks/pedestrian-lights
#
# TODO: Actually test this file, it's only been run in my head
################################################################

from machine import Pin
import time

# Timer Period - Edit this to change "Green" time.
timer_period = 180 # Set to 180 when Live

# 1 = Timer on. Works like a Pedestrian Crossing, press button
# and it goes green for timer_period seconds, then flashes red,
# then goes solid red until button pressed again.
# 0 = Timer off. Button toggles red/green lights (TODO: Finish This)
timer_mode = 1

# Set up the 2 relay pins
red_light = Pin(27, Pin.OUT)
green_light = Pin(28, Pin.OUT)

# Set up the physical button
pin = Pin(22, Pin.IN, Pin.PULL_UP)

# Button interrupt and debounce
interrupt_flag = 0
debounce_time = 0

# Ghetto State Machine
current_state = "Off"
states = ["Go", "Flash", "Stop", "Timer", "Boot"]

# My relays are active low, so in the below, off = on and on = off.
def change_state(state):
    current_state = state
    print('Currently in %s State' % current_state)
    print('Changed to %s State' % state)
    global red_light, green_light
    
    if state == "Go":
        red_light.on()
        green_light.off()
    elif state == "Flash":
        green_light.on()
        for i in range(16):
            red_light.off()
            time.sleep(0.2)
            red_light.on()
            time.sleep(0.2)
        change_state("Stop")
    elif state == "Stop":
        red_light.off()
        green_light.on()
    elif state == "Timer":
        red_light.on()
        green_light.off()
        time.sleep(timer_period)
        change_state("Flash")
    elif state == "Boot":
        for i in range(8):
            green_light.on()
            red_light.on()
            time.sleep(0.2)
            green_light.off()
            red_light.off()
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
        
        if timer_mode == 1:
            print("Timer Mode")
            change_state("Timer")
        else:
            print("Manual Mode")
            if current_state == "Stop":
                print("Stop State, Change to Go")
                change_state("Go")
            elif current_state == "Go":
                print("Go State, Change to Stop")
                change_state("Stop")
            else:
                print('State is %s' % current_state)
        # or rotate through available States:
        # state = states[(states.index(state) + 1) % len(states)]
        #change_state(state)
    time.sleep(0.1)  # Add a small delay to avoid high CPU usage

