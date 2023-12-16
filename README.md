# Pedestrian Lights

A Raspberry Pi Pico connected to a 240V Relay board with 2 relays, each of which are connected to 240V LED spotlights inside a set of Pedestrian Crossing lights (the red/green person lights to cross an intersection). I'll upload more details, photos, wiring diagrams etc Soon™.

## TODO

- Add timer functions, eg Green for 2 minutes, flash red for 30 seconds, then red for 2 minutes. Allow changing of timers via web interface.
- Add a physical button that lets you swap between Red/Green.
- Allow the user to choose whether the physical button swaps Red/Green, or initiates a one-off timer, eg "Green for 2 minutes then go Red".
- Make the web interface look like the lights themselves, pressing on a light toggles that light on/off.

## Notes

main.py requires a secrets.py file to be added alongside it, with these in it:

```
SSID = "WifiSSID"
PASS = "WifiPASS"
```
