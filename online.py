################################################################
# Pedestrian Lights Controller by Sen (Wifi-enabled Version)
# v 0.4 (dysfunctionally functional)
# https://github.com/senwerks/pedestrian-lights
#
# TODO: Better state-management of the light modes/status
# TODO: Make the webpage display current state of lights
#       even if changed by timer or physical button
# TODO: Better error/crash handling
################################################################

from machine import Pin, Timer
import network
import time
try:
    import usocket as socket
except ImportError:
    import socket
import secrets
import _thread

# Set up the 2 relay pins
relay1 = Pin(27, Pin.OUT)
relay1.value(0)
relay2 = Pin(28, Pin.OUT)
relay2.value(0)

# Set up the physical button
interrupt_flag = 0
debounce_time = 0
pin = Pin(22, Pin.IN, Pin.PULL_UP)
count = 0

# Connect to the network using SSID and PASS vars from secrets.py
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASS)
wait = 10

while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('Connecting to Wifi...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('Wifi Connection Failed!')
else:
    print('Connected to Wifi')
    ip = wlan.ifconfig()[0]
    print('IP:', ip)


################################################################
# Light Mode Functions
    
timer_mode = False

def relay_toggle():
    global relay1, relay2
    if relay1.value() == 0:
        relay1.value(1)
        relay2.value(0)
    else:
        relay1.value(0)
        relay2.value(1)

def toggle_timer_mode(relay_timer):
    global timer_mode
    if not timer_mode:
        timer_mode = True
        relay_timer.init(mode=Timer.PERIODIC, period=500, callback=lambda t: relay_toggle())
    else:    
        timer_mode = False
        relay_timer.deinit()

def start_timer_mode(relay_timer):
    global timer_mode
    if not timer_mode:
        timer_mode = True
        relay_timer.init(mode=Timer.PERIODIC, period=500, callback=lambda t: relay_toggle())

def stop_timer_mode(relay_timer):
    global timer_mode
    if timer_mode:
        timer_mode = False
        relay_timer.deinit()

relay_timer = Timer(-1)

def callback(pin):
    global interrupt_flag, debounce_time
    if (time.ticks_ms() - debounce_time) > 500:
        interrupt_flag = 1
        debounce_time = time.ticks_ms()

pin.irq(trigger=Pin.IRQ_FALLING, handler=callback)


################################################################
# Button Functions that run on Core 1

def button_thread():
    print("Button Thread Created!")

    global interrupt_flag, timer_mode
    
    while True:
        if interrupt_flag == 1:
            interrupt_flag = 0
            print("Button Pressed!")
            toggle_timer_mode(relay_timer)
        time.sleep(0.1)  # Add a small delay to avoid high CPU usage


################################################################
# Web Server functions that run on Core 2
        
def server_thread():
    print("Server Thread Created!")
    
    global relay1, relay2

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            conn.settimeout(None)
            request = str(request)
            print('Content = %s' % request)

            # Relay 1
            if '/relay1/on' in request:
                print('RELAY 1 ON')
                relay1.value(0)
            elif '/relay1/off' in request:
                print('RELAY 1 OFF')
                relay1.value(1)

            # Relay 2
            elif '/relay2/on' in request:
                print('RELAY 2 ON')
                relay2.value(0)
            elif '/relay2/off' in request:
                print('RELAY 2 OFF')
                relay2.value(1)

            # Timer Mode
            elif '/timer_mode/on' in request:
                print('Timer Mode ON')
                start_timer_mode(relay_timer)
            elif '/timer_mode/off' in request:
                print('Timer Mode OFF')
                stop_timer_mode(relay_timer)

            if relay1.value() == 1:
                relay1_state = ''
            else:
                relay1_state = 'checked'
            if relay2.value() == 1:
                relay2_state = ''
            else:
                relay2_state = 'checked'
                
            html = """
            <html>
                <head>
                    <title>Pedestrian Lights</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body{font-family:Arial; text-align: center; margin: 0px auto; padding-top:30px;}
                        .switch{position:relative;display:inline-block;width:120px;height:68px}
                        .switch input{display:none}
                        .slider{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#ccc;border-radius:34px}
                        .slider:before{position:absolute;content:"";height:52px;width:52px;left:8px;bottom:8px;background-color:#fff;-webkit-transition:.4s;transition:.4s;border-radius:68px}
                        input:checked+.slider{background-color:#2196F3}
                        input:checked+.slider:before{-webkit-transform:translateX(52px);-ms-transform:translateX(52px);transform:translateX(52px)}
                    </style>

                    <script>
                        function toggleTimerMode(element) {
                            var xhr = new XMLHttpRequest();
                            var manualSwitch1 = document.getElementById('manualSwitch1');
                            var manualSwitch2 = document.getElementById('manualSwitch2');

                            if (element.checked) {
                                xhr.open("GET", "/timer_mode/on", true);
                                manualSwitch1.disabled = true;
                                manualSwitch2.disabled = true;
                            } else {
                                xhr.open("GET", "/timer_mode/off", true);
                                manualSwitch1.disabled = false;
                                manualSwitch2.disabled = false;
                            }
                            xhr.send();
                        }
                        function toggleCheckbox(element, relayNum) {
                            var xhr = new XMLHttpRequest();
                            if(element.checked){
                                xhr.open("GET", "/relay" + relayNum + "/on", true);
                            } else {
                                xhr.open("GET", "/relay" + relayNum + "/off", true);
                            }
                            xhr.send();
                        }
                    </script>
                </head>
                <body>
                    <h1>Pedestrian Lights</h1>

                    <h2>Red Light</h2>
                    <label class="switch">
                        <input type="checkbox" id="manualSwitch1" onchange="toggleCheckbox(this, '1')" %s>
                        <span class="slider"></span>
                    </label>
                    
                    <h2>Green Light</h2>
                    <label class="switch">
                        <input type="checkbox" id="manualSwitch2" onchange="toggleCheckbox(this, '2')" %s>
                        <span class="slider"></span>
                    </label>
                    
                    <h2>Timer Mode</h2>
                    <label class="switch">
                        <input type="checkbox" id="timerSwitch" onchange="toggleTimerMode(this)" %s>
                        <span class="slider"></span>Timer Mode
                    </label>
                </body>
            </html>""" % (relay1_state, relay2_state, 'checked' if timer_mode else '')

            response = html
            
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()

        except OSError as e:
            conn.close()
            print('Connection closed')


################################################################
# Now let's run everything!

if __name__ == "__main__":
    try:
        new_thread = _thread.start_new_thread(button_thread, ())
        server_thread()

    except KeyboardInterrupt:
        machine.reset()


