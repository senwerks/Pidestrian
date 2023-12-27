# Pedestrian Lights

A Raspberry Pi Pico connected to a 240V Relay board with 2 relays, each of which are connected to 240V LED spotlights inside a set of Pedestrian Crossing lights (the red/green person lights to cross an intersection). I'll upload more details, photos, wiring diagrams etc Soon™.

## TODO

- Add timer functions, eg Green for 2 minutes, flash red for 30 seconds, then red for 2 minutes. Allow changing of timers via web interface.
- Add a physical button that lets you swap between Red/Green.
- Allow the user to choose whether the physical button swaps Red/Green, or initiates a one-off timer, eg "Green for 2 minutes then go Red".
- Make the web interface look like the lights themselves, pressing on a light toggles that light on/off.

## Notes

There's an "online.py" and "offline.py", the former connects to Wifi and serves a web app with controls for the lights, and the latter is a simpler timer based system using a physical button to trigger mode changes.

Rename one to "main.py" and copy it to the RPi Pico (online.py requires a Pico W, offline.py can use a Pico W or normal Pico). Read the notes in the files for config changes.