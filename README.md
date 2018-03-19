## About
There was no Linux software available for the PowerWalker PDU and ATS, but the [manufacturer](https://powerwalker.com/) was kind enough to supply me with what I needed to make my own library.

![PowerWalker PDU and ATS in my homelab](media/homelab.jpg)

I'm using a Raspberry Pi as my power manager, it is connected to both the PDU and ATS. I'm planning to use MQTT to communicate with it, and report power usage etc. to things like Home Assistant. For graphing I'll be storing values in Elasticsearch and displaying the data using Kibana.

**Beta!** This library is still very much in beta, and not all features are implemented yet.

## PowerWalker PDU RC-16A IEC
![PowerWalker PDU RC-16A IEC](media/powerwalker_pdu_rc-16a.jpg)

PowerWalker PDU RC-16A is designed to distribute AC power from a single source to 8 outputs with advanced load monitoring and local or remote ON/OFF switching control of individual outlets.

https://powerwalker.com/?lang=en&page=product&item=10133001

### Available commands
* `connect`: Connect to PDU device.
* `send`: Send custom command.
* `info`: Get and return device information.
* `status`: Get and return device statuses. (see codes below)
* `power_watt`: Get and return active power measurements for input and all outputs.
* `power_va`: Get and return apparent power measurements for input and all outputs.
* `test`: Test PDU device, turn on all LEDs and the buzzer for 5 seconds.

> Changing output states not yet implemented.

#### Output status codes
0. Off
1. On
2. Shutdown active
3. Shutdown imminent (S01-S08 code)
4. Restore active
5. Overload alarm (F01-F08 code)
6. Locked (L01-L08 code)

## PowerWalker ATS
![PowerWalker ATS](media/powerwalker_ats.jpg)

ATS (Automatic Transfer Switch) supports connection of two independent power sources. If primary power source fails, the secondary will automatically back up the connected load without any interruption. 

https://powerwalker.com/?page=product&item=10120543&lang=en

### Available commands
* `connect`: Connect to PDU device.
* `send`: Send custom command.
* `info`: Get and return device information.
* `status`: Get and return device statuses.

> Changing perferred input not yet implemented.

## Scripts
* `status.py`: Get and print statuses
* `info.py`: Get and print device information
* `mqtt.py`: Publishing values to a MQTT broker
