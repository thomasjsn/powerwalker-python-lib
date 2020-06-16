# About
> Software ___is not developed___ by BlueWalker GmbH.

There was no Linux software available for the PowerWalker PDU and ATS, but the [manufacturer](https://powerwalker.com/) was kind enough to supply me with what I needed to make my own library.

![PowerWalker PDU and ATS in my homelab](media/homelab_ats_pdu_front.jpg)

I'm using a Raspberry Pi as a power manager in my [homelab](https://link.stdout.no/3), it is connected to both the PDU and ATS. It's best practice to have a single application responsible for communicating with the devices, as you will get communication errors if two applications tries to talk to the same device at the same time.

I am using the `mqtt.py` script to publish ATS and PDU data on the MQTT network. Then you can have multiple clients subscribe to the respective MQTT topics, like [Home Assistant](https://home-assistant.io/). To visualize the data I use the [Home Assistant InfluxDB component](https://www.home-assistant.io/components/influxdb/), then [Grafana](https://grafana.com/) pulls the data from [InfluxDB](https://www.influxdata.com/) and makes [cool graphs](media/homelab_servers_grafana.jpg).

To make sure that the `mqtt.py` script keeps running; I'm using [Supervisor](http://supervisord.org/).

**Note!** Methods and keys may change; as I am still investigating use cases and best practices.

## Communicate
Connect either the USB or the serial port, find the correct device path and instantiate:

```py
import powerwalker

pdu = powerwalker.PDU("/dev/ttyUSB0")
ats = powerwalker.ATS("/dev/ttyUSB1")
```

There's a chance that your device is not being recognized as usbserial. Therefore, you have to instantiate as usbhid device:

```py
import powerwalker

pdu = powerwalker.PDU("/dev/hidraw0", usbhid=True)
ats = powerwalker.ATS("/dev/hidraw1", usbhid=True)
```


# PowerWalker PDU RC-16A IEC
![PowerWalker PDU RC-16A IEC front](media/powerwalker_pdu_rc-16a_front.jpg)
![PowerWalker PDU RC-16A IEC back](media/powerwalker_pdu_rc-16a_back.jpg)

PowerWalker PDU RC-16A is designed to distribute AC power from a single source to 8 outputs with advanced load monitoring and local or remote ON/OFF switching control of individual outlets.

https://powerwalker.com/?item=10133001

## Available methods
| Method | Description | Type |
| --- | --- | --- |
| `connect()` | Connect to PDU device. | - |
| `send(cmd)` | Send custom command. | - |
| `info()` | Get and return device information. | get |
| `status()` | Get and return device statuses. (see codes below) | get |
| `power_w()` | Get and return active power (W) measurements for input and all outputs. | get |
| `power_va()` | Get and return apparent power (VA) measurements for input and all outputs. | get |
| `energy_kwh()` | Get and return energy consumption (kWh) for input and all outputs. | get |
| `energy_kwh_clear()` | Clear energy consumption values for input and all outputs. | **set** |
| `countdown_times()` | Get and return shutdown and restore countdown times for all outputs. | get |
| `shutdown(idx, shdn)` | Shutdown output `idx` in `shdn` minutes. | **set** |
| `shutdown_restore(idx, shdn, rst)` | Shutdown output `idx` in `shdn` minutes, restore power after `rst` minutes. | **set** |
| `shutdown_cancel(idx)` | Cancel pending shutdown on output `idx`. | **set** |
| `protocol()` | Get and return device protocol ID. | get |
| `firmware()` | Get and return device firmware version. | get |
| `test()` | Test PDU device, turn on all LEDs and the buzzer for 5 seconds. | **set** |
| `memory_get(adr)` | Get and return memory setting at `adr` location. | get |

### Output status codes
0. Off
1. On
2. Shutdown active
3. Shutdown imminent (S01-S08 code)
4. Restore active
5. Overload alarm (F01-F08 code)
6. Locked (L01-L08 code)

### Shutdown method arguments
* `idx` : output; `1` to `8`, `A` for all.
* `shdn` : shutdown delay in minutes; `0.1` to `0.9`, `1` to `99`, `0` for immediate.
* `rst` : restore delay in minutes; `1` to `9999`, `0` for 1 second.

### Memory configuration map
| Adr | Key | Unit | Min | Max | Default |
| --- | --- | ---- | --- | --- | ------- |
| 0 | `output_start_up_delay` | sec | 0 | 240 | 1 |
| 1 | `out1_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 2 | `out2_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 3 | `out3_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 4 | `out4_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 5 | `out5_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 6 | `out6_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 7 | `out7_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 8 | `out8_current_alarm` | 0.1 A | 0.5 | 4.0 | 2.0 |
| 9 | `low_input_voltage_alarm` | V | 184 | 207 | 196 |
| 10 | `high_input_voltage_alarm` | V | 242 | 264 | 253 |
| 11 | `max_input_voltage_shutoff` | V | 253 | 300 * | 276 |
| 12 | `low_input_current_alarm` | 0.1 A | 0.0 | 15.0 | 0.0 |
| 13 | `high_input_current_alarm` | 0.1 A | 1.0 | 16.0 | 16.0 |
| 14 | `shutdown_imminent_signal` | min | 1 | - | 3 |

    * 0xFFFF = disabled
    
#### Output configuration byte
Memory address 1 to 8 also contains output configuration byte, key: `out?_config`.

| Byte | Dec | Description | `0` | `1` |
| ---- | --- | ----------- | --- | --- |
| 0 | 1 | Output status at power on | off | on |
| 1 | 2 | Automatic disconnection of the output 1 minute after the overload alarm | enabled | disabled |
| 2 | 4 | On/off button enabled on front panel | disabled | enabled |
| 3 | 8 | Not in use | - | - |
| 4 | 16 | Not in use | - | - |
| 5 | 32 | Not in use | - | - |
| 6 | 64 | Not in use | - | - |
| 7 | 128 | Not in use | - | - |

## Example responses

### Generic
* `ACK` if command was accepted.
* `NAK` if command was **not** accepted.

### `info()`
```py
{   'in_out_phase': '1/1',
    'in_socket_no': '1',
    'model': '############PDU',
    'nom_in_voltage': '230',
    'nom_out_voltage': '230',
    'out_socket_no': '8'}
```

### `status()`
```py
{   'in_current': 2.1,
    'in_freq': 49.8,
    'in_voltage': 225.5,
    'int_temp': 36.0,
    'out1_current': 0.4,
    'out2_current': 0.5,
    'out3_current': 0.3,
    'out4_current': 0.1,
    'out5_current': 0.2,
    'out6_current': 0.2,
    'out7_current': 0.3,
    'out8_current': 0.0,
    'status': {   'a01_low_in_voltage': 0,
                  'a02_high_in_voltage': 0,
                  'f09_low_in_current': 0,
                  'f10_high_in_current': 0,
                  'f11_pwr_fail_aux1': 0,
                  'f12_pwr_fail_aux2': 0,
                  'na_b8': 0,
                  'na_b9': 0,
                  'out1_status': 1,
                  'out2_status': 1,
                  'out3_status': 1,
                  'out4_status': 1,
                  'out5_status': 1,
                  'out6_status': 1,
                  'out7_status': 1,
                  'out8_status': 1}}
```

### `power_w()`
```py
{   'in_w': 441,
    'out1_w': 62,
    'out2_w': 108,
    'out3_w': 74,
    'out4_w': 37,
    'out5_w': 39,
    'out6_w': 33,
    'out7_w': 57,
    'out8_w': 0}
```

### `power_va()`
```py
{   'in_va': 478,
    'out1_va': 108,
    'out2_va': 123,
    'out3_va': 83,
    'out4_va': 47,
    'out5_va': 43,
    'out6_va': 65,
    'out7_va': 70,
    'out8_va': 0}
```

### `energy_kwh()`
```py
{   'in_kwh': 725.9,
    'out1_kwh': 4.3,
    'out2_kwh': 103.4,
    'out3_kwh': 17.4,
    'out4_kwh': 114.0,
    'out5_kwh': 201.9,
    'out6_kwh': 106.8,
    'out7_kwh': 47.6,
    'out8_kwh': 19.8}
```

### `countdown_times()`
```py
{   'out1_cd_sec': {'r': 0, 's': 0},
    'out2_cd_sec': {'r': 0, 's': 0},
    'out3_cd_sec': {'r': 0, 's': 0},
    'out4_cd_sec': {'r': 0, 's': 0},
    'out5_cd_sec': {'r': 0, 's': 0},
    'out6_cd_sec': {'r': 0, 's': 0},
    'out7_cd_sec': {'r': 0, 's': 0},
    'out8_cd_sec': {'r': 0, 's': 0}}
```

### `protocol()`
```py
{'prot_id': 'PI90'}
```

### `firmware()`
```py
{'verfw': 0.15}
```

### `memory_get(0)`
```py
{'output_start_up_delay': 1}
```

### `memory_get(1)`
```py
{'out1_config': 255, 'out1_current_alarm': 20}
```

# PowerWalker ATS
![PowerWalker ATS front](media/powerwalker_ats_front.jpg)
![PowerWalker ATS back](media/powerwalker_ats_back.jpg)

ATS (Automatic Transfer Switch) supports connection of two independent power sources. If primary power source fails, the secondary will automatically back up the connected load without any interruption. 

https://powerwalker.com/?item=10120543

## Available methods
| Method | Description | Type |
| --- | --- | --- |
| `connect()` | Connect to PDU device. | - |
| `send(cmd)` | Send custom command. | - |
| `info()` | Get and return device information. | get |
| `status()` | Get and return device statuses. | get |
| `protocol()` | Get and return device protocol ID. | get |
| `firmware()` | Get and return device firmware version. | get |
| `memory_get(adr)` | Get and return memory setting at `adr` location. | get |

### Memory configuration map
| Adr | Key | Unit | Min | Max | Default |
| --- | --- | ---- | --- | --- | ------- |
| 0 | `src1_voltage_high_loss` | V | 100 | 300 | 258 |
| 1 | `src1_voltage_high_back` | V | 100 | 300 | 248 |
| 2 | `src1_voltage_low_loss` | V | 100 | 300 | 180 |
| 3 | `src1_voltage_low_back` | V | 100 | 300 | 190 |
| 4 | `src1_freq_high_loss` | Hz | 40 | 70 | 55 |
| 5 | `src1_freq_high_back` | Hz | 40 | 70 | 0 |
| 6 | `src1_freq_low_loss` | Hz | 40 | 70 | 45 |
| 7 | `src1_freq_low_high` | Hz | 40 | 70 | 0 |
| 8 | `src2_voltage_high_loss` | V | 100 | 300 | 258 |
| 9 | `src2_voltage_high_back` | V | 100 | 300 | 248 |
| 10 | `src2_voltage_low_loss` | V | 100 | 300 | 180 |
| 11 | `src2_voltage_low_back` | V | 100 | 300 | 190 |
| 12 | `src2_freq_high_loss` | Hz | 40 | 70 | 55 |
| 13 | `src2_freq_high_back` | Hz | 40 | 70 | 0 |
| 14 | `src2_freq_low_loss` | Hz | 40 | 70 | 45 |
| 15 | `src2_freq_low_high` | Hz | 40 | 70 | 0 |
| 16 | `overload_alarm` | % | 0 | 150 | 100 |
| 17 | `overload_fault` | % | 0 | 250 | 0 |
| 18 | `acceptable_phases` | ° | 0 | 180 | 0 |
| 19 | `breaking_time` | ms | 0 | 9999 | 5 |
| 20 | `blanking_time` | ms | 0 | 1000 | 4 |

## Example responses

### `info()`
```py
{   'battery_voltage': '---.-',
    'rated_output_current': '016',
    'rated_output_freq': '50.0',
    'rated_output_voltage': '230.0'}
```

### `status()`
```py
{   'int_temp': 35.0,
    'out_current': 2.2,
    'out_load_pct': 14.0,
    'src1_freq': 50.0,
    'src1_voltage': 227.3,
    'src2_freq': 50.0,
    'src2_voltage': 227.3,
    'status': {   'aux_pwr1_fail': 0,
                  'aux_pwr2_fail': 0,
                  'na_c0': 0,
                  'na_c1': 0,
                  'na_c2': 0,
                  'na_c3': 0,
                  'na_c4': 0,
                  'na_c5': 0,
                  'na_c6': 0,
                  'na_c7': 0,
                  'on_fault_mode': 0,
                  'on_src1': 1,
                  'on_src2': 0,
                  'overload_alarm': 0,
                  'overload_fault': 0,
                  'preferred_src2': 0,
                  'short_fault': 0,
                  'src1_freq_bad': 0,
                  'src1_voltage_bad': 0,
                  'src1_wave_bad': 0,
                  'src2_freq_bad': 0,
                  'src2_voltage_bad': 0,
                  'src2_wave_bad': 0,
                  'syncron_bad': 0},
    'sync_angle': 1.0}
```

### `protocol()`
```py
{'prot_id': 'PI97'}
```

### `firmware()`
```py
{'verfw': 181.0}
```

### `memory_get(0)`
```py
{'src1_voltage_high_loss': 258}
```

# CLI
For easy access to the device methods; use `cli.py`:

    $ python3 cli.py device method arguments

## Examples
Run test sequence on PDU:

    $ python3 cli.py pdu test

Shutdown output 8 in 0.5 minutes:

    $ python3 cli.py pdu shutdown 8 0.5

Shutdown output 8 in 2 minutes, restore after 1 second:

    $ python3 cli.py pdu shutdown_restore 8 2 0

Cancel pending shutdown on output 8

    $ python3 cli.py pdu shutdown_cancel 8

# MQTT
To publish ATS and PDU data to MQTT; use `mqtt.py`:

    $ python3 mqtt.py

Make sure to rename `config.sample.py` to `config.py` and set the correct settings.

## Outlet state change (PDU)
The MQTT script subscribes to `cfg.mqtt['prefix'] + "/pdu/outlet/+/+"`; to change the state of an outlet use topic:

    your_prefix/pdu/outlet/out[1-8]/set

Payload can be `0`, `1` or anything that Python casts as a boolean value.

All incoming commands are queued so not to interrupt any ongoing serial communication,
at the start of each loop cycle all pending commands are performed.

Note that the state change is not immediate, there is a slight delay were the PDU warn of outlet imminent shutdown.
Also note that if an outlet is not listed in the config file as "allowed state change"; a `ValueError` exception is raised.

## Sample topics
```py
pdu/outlet/out1 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out2 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out3 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out4 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out5 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out6 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out7 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/outlet/out8 {"shutdown_sec": 0, "state": "On", "status": 1, "restore_sec": 0}
pdu/status {"pwr_fail_aux2": 0, "low_in_voltage": 0, "pwr_fail_aux1": 0, "high_in_current": 0, "temp_c": 33.0, "low_in_current": 0, "in_hz": 49.8, "high_in_voltage": 0, "in_v": 228.2}
pdu/power/out1 {"va": 95, "w": 76, "a": 0.4}
pdu/power/out6 {"va": 0, "w": 0, "a": 0.0}
pdu/power/out7 {"va": 0, "w": 0, "a": 0.0}
pdu/power/out2 {"va": 0, "w": 0, "a": 0.0}
pdu/power/out3 {"va": 92, "w": 89, "a": 0.4}
pdu/power/out8 {"va": 0, "w": 0, "a": 0.0}
pdu/power/in {"va": 318, "w": 266, "a": 1.4}
pdu/power/out5 {"va": 65, "w": 60, "a": 0.2}
pdu/power/out4 {"va": 63, "w": 50, "a": 0.1}
ats/supply/src1 {"preferred": 1, "hz": 50.0, "bad": "0", "active": 1, "v": 229.7}
ats/supply/src2 {"preferred": 0, "hz": 50.0, "bad": "0", "active": 0, "v": 230.9}
ats/status {"out_pct": 10.0, "overload_alarm": 0, "overload_fault": 0, "out_a": 1.4, "syncron_bad": 0, "aux_pwr2_fail": 0, "sync_angle": 1.0, "temp_c": 32.0, "on_fault_mode": 0, "short_fault": 0, "aux_pwr1_fail": 0}
```

# Script files
* `cli.py`: Simple command line interface.
* `mqtt.py`: Publishing values to MQTT.
* `ups.py`: Get UPS data from `upsc` and publish to MQTT.

# Useful resources
* [Persistent names for usb-serial devices](http://hintshop.ludvig.co.nz/show/persistent-names-usb-serial-devices/)

# Author
[Thomas Jensen](https://thomas.stdout.no)

# Notices
* PowerWalker is a brand of BlueWalker GmbH.
* PowerWalker PDU RC-16A IEC and PowerWalker ATS are products of BlueWalker GmbH.
* Software is not developed by BlueWalker GmbH.
* This library is published under the [MIT license](LICENSE).
