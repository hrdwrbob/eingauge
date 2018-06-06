
# Wiring
This details wiring I used in my implementation of eingauge for my AUDM 2005 Subary Liberty GT. This is a good starting point, but is mainly documentation for my reference.

Overall hardware/wiring design:

```
Ethanol sensor arduino \
                       |
Sensors->loom plug in engine bay->Arduino->dash stepper motors(boost/tach/speed)
                                   |    |
                                   |    |-Thermocouple amplifier
                                   |    |
Car power->Power management box --/     MCP2515(CAN)----car canbus
                        |                              |
    5" touchscreen----Raspberry pi---MCP2515(CAN)------/
                         |
                      128x96 OLED in dash.              
```
## Power box.
I have a power box that manages power. It performs the following functions:
* Voltage divider to measure the cars voltage 
* 5V power supply
* 5V signals on/off for IGN and Illum.
* Auto switches the arduino power on when IGN is turned on. 
* 4 relays (controlled by arduino) that switch arduino/pi/clock/screen power output.
* Overall power switch to isolate entire system
* power switch to turn on all relays (for testing/override)

The idea is that the arduino would only turn itself off if the voltage drops super low or there's a power outage, but it needs the IGN power on to bootstrap it and turn it on. The power timeout on the pi would probably be configurable, but the pi screen can turn off with IGN.

### Power connector from radio
This is the tail that comes out from behind the radio to feed the power box.

Colour | Meaning
------------ | -------------
Red | IGN
Black/brown | GND
Yellow | Illum
White/green | Constant +12V

### Power box arduino pin output
power box | description | Wire colour
------------ | ------------- | -------------
Relay 1 | Arduino | Yellow
Relay 2 | pi | Green
Relay 3 | pi screen | Blue
Relay 4 | Clock | Purple
Digital out | IGN | Grey
Digital out | Illum | White
Analog out  | +12V with 220k/100k voltage divider | Black


## Pi pinout, including display and CAN module.

### Pi 40 pin plug.
The pi has a plug that cycles colours every 10 pins, here's the key:

Pin | colour
------------ | -------------
1 | black
2 | white
3 | grey
4 | purple
5 | blue
6 | green
7 | yellow
8 | orange
9 | red
0 | brown


### Ribbon cable from OLED dash display
Colour| Meaning
------------ | -------------
Light brown | GND
Red | +5V
Orange | CD (NOT REQUIRED)
Yellow | RST
Green | DNC (DC)
Blue | CLK
Purple | MOSI

### Grey Ribbon cable order (starting from red wire):
Number| Meaning
------------ | -------------
1 | GND
2 | +5V
3 | OC (CS)
4 | RST
5 | DC
6 | CL (SCK)
7 | SI (MOSI)




### Raspberry Pi OLED Display pins

Pin Number|description|colour|Number on the ribbon cable
------------ | ------------- | -------------| -------------
2 | +5V | white | 2
6 | GND | green | 1
18 | (GPIO 24) RST | orange | 4
19 | MOSI | red | 7
22 | (GPIO 25) DNC | white | 5
23 | CLK | grey | 6
24 | CS/OC | purple | 3


### Raspberry Pi MCP2515 pin output
* is shared with display SPI

Pin Number|description|colour pi|colour MCP2515|MCP2515 description
------------ | ------------- | ------------- | ------------- | -------------
pin | num| (pi | desc) | colour | 2515
1| +3.3V | black | orange | Vcc
3| +5V | white | red | +5V | (CAN | chip)
6*| GND | green | black | GND
19*| MOSI | red | blue | SI
21| MISO | black | green | SO
23*| CLK | grey | purple | SCK
26| SPIO.CE1 | green | yellow | CS
32| IO12 | white | grey | INT






## Arduino wiring

### Incoming wiring tails from engine bay
Colours | colour |purpose
------------ | ------------- | -------------
red/black| | power.
green/white/black | green | map 
green/white/black | white | oil pressure
black | white | fuel pressure
green/black | | water temp
blue/black | | IAT preIC
white/black | | IAT postIC
yellow/black | | EGT
brown/black/orange | orange/black | Oil temp,
brown/black/orange |   Brown | Ethanol content.

### Engine bay harness connector
```
1234
5678
9ABC
DEFG
```

 Pin | purpose | Colour
 ------------ | ------------- | -------------
1|+5V | red
2|GND |black
3|MAP sensor| green
4|oil pressure| white
5|fuel pressure| yellow
7-8 |water temp |green/black
9-a | IAT preIC | white/black
B-C |IAT postIC  | blue/black
E | Ethanol content | orange
FG | EGT | yellow/black 

### Junction block for arduino
Pin | Description | detail
------------ | ------------- | -------------
1 | +5V| (Shared for +5V,and all resistance sensors)
2 | GND|
3 | MAP | (analog direct)
4 | Oil pressure | (analog direct)
5 | Fuel pressure | (analog direct)
6 | Water temp GND | (voltage divider 10k)
7 | IAT preIC GND | (voltage divider 1k)
8 | IAT postIC GND | (voltage divider 1k)
9 | Oil temp GND | (voltage divider 10k)
10 | AFR | (analog direct)
11 | EGT |
12 | EGT |

## Arduino  inputs

### Arduino analog
Pin | Description | Colour
------------ | ------------- | -------------
A0 | MAP | Brown 
A1 | Oil pressure | red
A2 | Fuel pressure | orange
A3 | Water temp | yellow
A4 | IAT preIC | green
A5 | IAT postIC | blue
A6 | MAP reference | purple
A7 | Oil Temp | grey
A8 | AFR | white
A15 | +12V reference 220k/100k voltage divider - from power box | black

### Arduino PWM outputs:

Pin | Description | Colour
------------ | ------------- | -------------
PWM2-5 | Boost gauge | green heatshrink
PWM6-9 | Tacho | red heatshrink 
PWM10-13 | Speedo | Black heatshrink

### Arduino Digital inputs/outputs:

Pin | Description | Colour
------------ | ------------- | -------------
I51 | Lights sense | grey
I53 | Ignition sense | white
O31 | Arduino power relay | Yellow
O33 | Pi power relay | Green
O35 | screen power relay) | Blue
O37 | Clock power relay | Purple
O22 | CS Thermocouple. | Purple
I24 | Interrupt MCP2515 | Orange
O26 | CS MCP2515  | Red



Arduino ISCP plug

```
^ To mega chip.
123
456
```
Maps to flat cable starting at red using A-F
Flat cable starting at red #1

ISCP pin | Description | pin
------------ | ------------- | -------------
A | MISO (red) | 3
B | VCC (+5V) | 6
C | Clock | 2
D | MOSI | 5
E | Reset (NC) | 1
F | GND | 4

## CAN Wiring

High speed CAN between BIU and ECU (page 131 of wiring manual)
```
BIU...
B280 plug
far right of connector.
B30L blue (CAN L)
B20R Red ( CAN H)
```
Goes to both MCP2515 boards.

