from machine import Pin, Timer
import network
import time
try:
    import usocket as socket
except ImportError:
    import socket
import secrets

redlight = Pin(27, Pin.OUT)
redlight.value(0)

greenlight = Pin(28, Pin.OUT)
greenlight.value(0)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASS) # From secrets.py

# Connect to the network
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

timer_mode = False  # Flag for timer mode

def relay_toggle(timer):
    global redlight, greenlight
    if redlight.value() == 0:
        redlight.value(1)
        greenlight.value(0)
    else:
        redlight.value(0)
        greenlight.value(1)

def start_timer_mode():
    global timer_mode
    if not timer_mode:
        timer_mode = True
        relay_timer.init(mode=Timer.PERIODIC, period=500, callback=relay_toggle)

def stop_timer_mode():
    global timer_mode
    if timer_mode:
        timer_mode = False
        relay_timer.deinit()

relay_timer = Timer(-1)


def web_server():
    if redlight.value() == 1:
        redlight_state = ''
    else:
        redlight_state = 'checked'
    if greenlight.value() == 1:
        greenlight_state = ''
    else:
        greenlight_state = 'checked'
        
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
    </html>""" % (redlight_state, greenlight_state, 'checked' if timer_mode else '')

    return html


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
        if '/redlight/on' in request:
            print('RELAY 1 ON')
            redlight.value(0)
        elif '/redlight/off' in request:
            print('RELAY 1 OFF')
            redlight.value(1)

        # Relay 2
        elif '/greenlight/on' in request:
            print('RELAY 2 ON')
            greenlight.value(0)
        elif '/greenlight/off' in request:
            print('RELAY 2 OFF')
            greenlight.value(1)

        # Timer Mode
        elif '/timer_mode/on' in request:
            print('Timer Mode ON')
            start_timer_mode()
        elif '/timer_mode/off' in request:
            print('Timer Mode OFF')
            stop_timer_mode()

        response = web_server()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')


