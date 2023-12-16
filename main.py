from machine import Pin
import network
import time
try:
    import usocket as socket
except ImportError:
    import socket
import secrets

relay1 = Pin(27, Pin.OUT)
relay2 = Pin(28, Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASS)  # ssid, password

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


def web_server():
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
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body{font-family:Arial; text-align: center; margin: 0px auto; padding-top:30px;}
                .switch{position:relative;display:inline-block;width:120px;height:68px}.switch input{display:none}
                .slider{position:absolute;top:0;left:0;right:0;bottom:0;background-color:#ccc;border-radius:34px}
                .slider:before{position:absolute;content:"";height:52px;width:52px;left:8px;bottom:8px;background-color:#fff;-webkit-transition:.4s;transition:.4s;border-radius:68px}
                input:checked+.slider{background-color:#2196F3}
                input:checked+.slider:before{-webkit-transform:translateX(52px);-ms-transform:translateX(52px);transform:translateX(52px)}
            </style>
            <script>
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
            <label class="switch">
                <input type="checkbox" onchange="toggleCheckbox(this, '1')" %s>
                <span class="slider"></span>
            </label>
            <label class="switch">
                <input type="checkbox" onchange="toggleCheckbox(this, '2')" %s>
                <span class="slider"></span>
            </label>
        </body>
    </html>""" % (relay1_state, relay2_state)

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
        if '/relay1/on' in request:
            print('RELAY 1 ON')
            relay1.value(0)
        elif '/relay1/off' in request:
            print('RELAY 1 OFF')
            relay1.value(1)
        elif '/relay2/on' in request:
            print('RELAY 2 ON')
            relay2.value(0)
        elif '/relay2/off' in request:
            print('RELAY 2 OFF')
            relay2.value(1)

        response = web_server()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    except OSError as e:
        conn.close()
        print('Connection closed')
