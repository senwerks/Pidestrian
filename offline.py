################################################################
# Pedestrian Lights Controller by Sen (Offline Version)
# v 0.1 (simply simple)
# https://github.com/senwerks/pedestrian-lights
#
# TODO: Actually test this file, it's only been run in my head
################################################################

from machine import Pin, Timer
import time

# Timer Period - Edit this to change "Green" time.
timer_period = 1000 # Set to 120000 when Live

# Set up the 2 relay pins
relay1 = Pin(27, Pin.OUT)
relay1.value(0)
relay2 = Pin(28, Pin.OUT)
relay2.value(0)

# Set up the physical button
pin = Pin(22, Pin.IN, Pin.PULL_UP)

# Button interrupt and debounce
interrupt_flag = 0
debounce_time = 0

# Ghetto State Machine (most aren't being used yet but are for future plans)
state = "Off"
states = ["Off", "On", "Go", "Stop", "Timer"]

relay1_timer = Timer(-1)
relay2_timer = Timer(-1)

def change_state(state):
    global relay1, relay2, relay1_timer, relay2_timer
    if state == "Off":
        relay1.value(0)
        relay2.value(0)
        relay1_timer.deinit()
        relay2_timer.deinit()
    elif state == "On":
        relay1.value(1)
        relay2.value(1)
        relay1_timer.deinit()
        relay2_timer.deinit()
    elif state == "Go":
        relay1.value(1)
        relay2.value(0)
        relay1_timer.deinit()
        relay2_timer.deinit()
    elif state == "Flash":
        relay1_timer.deinit()
        relay2_timer.deinit()
        for i in range(10):
            relay2.value(1)
            time.sleep(0.25)
            relay2.value(0)
            time.sleep(0.25)
        change_state("Stop")
    elif state == "Stop":
        relay1.value(0)
        relay2.value(1)
        relay1_timer.deinit()
        relay2_timer.deinit()
    elif state == "Timer":
        relay1.value(1)
        relay2.value(0)
        relay1_timer.deinit()
        relay2_timer.deinit()
        relay1_timer.init(mode=Timer.ONE_SHOT, period=timer_period, callback=lambda t: change_state("Flash"))

def callback(pin):
    global interrupt_flag, debounce_time
    if (time.ticks_ms() - debounce_time) > 500:
        interrupt_flag = 1
        debounce_time = time.ticks_ms()

pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)

# Time to put it all together...

while True:
    if interrupt_flag == 1:
        interrupt_flag = 0
        print("Button Pressed!")
        state = states[(states.index(state) + 1) % len(states)]
        change_state(state)
        print("State:", state)
        
    time.sleep(0.1)  # Add a small delay to avoid high CPU usage
