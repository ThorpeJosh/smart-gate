# Raspberry pi powered smart gate
This repo is for a private application of a IOT inspired raspberry pi controller for a household front gate
The gate has 3 input buttons to operate it, a 24V motor, a 24V battery with solar charging, and wifi for internet connectivity.

## GPIO inputs
* 3 push-buttons (NO, Closed grounds the pin)
  * Outside the property, activated when entering
  * Inside the property, activated when exiting
  * On the control box mounted on the gate post, used for debugging
* ADS1115 via I2C
  * Shunt voltage to measure current through motor for hit detection
  * Battery voltage for logging

## GPIO outputs
* Gate Motor (2 pins, driving SPDT relays in a H-bridge configuration

## Connectivity
Raspberry pi is fitted with a wifi radio and is connected to a personal VPN for remote access and control

## Modes
Gate has 3 modes it can operate in
  * Normal - Closed unless a button is pushed then it opens for a period of time then closes again.
    If the gate hits an object when opening, it will stop the motor and wait for another button push.
    If the gate hits an object when closing, it will re-open.
  * Permanently Open - Gate opens and stays there until mode is changed
  * Permanently Closed - Gate closes and stays there until mode is changed
  
## Working on this repository


