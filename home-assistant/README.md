# Home Assistant examples
I am using [Home-Assistant](https://home-assistant.io/) to show data from my ATS and PDU, here is some of my config.

## Sensors
```yml
sensor:

  - platform: mqtt
    state_topic: 'homelab/pdu/power/out1'
    name: PDU power 1
    unit_of_measurement: 'W'
    value_template: "{{ value_json.w }}"
    json_attributes_topic: 'homelab/pdu/power/out1'

  - platform: mqtt
    state_topic: 'homelab/pdu/power/out2'
    name: PDU power 2
    unit_of_measurement: 'W'
    value_template: "{{ value_json.w }}"
    json_attributes_topic: 'homelab/pdu/power/out2'

  - platform: mqtt
    name: "PDU outlet 1"
    state_topic: "homelab/pdu/outlet/out1"
    value_template: "{{ value_json.state }}"
    json_attributes_topic: "homelab/pdu/outlet/out1"

  - platform: mqtt
    name: "PDU outlet 2"
    state_topic: "homelab/pdu/outlet/out2"
    value_template: "{{ value_json.state }}"
    json_attributes_topic: "homelab/pdu/outlet/out2"

  - platform: mqtt
    state_topic: 'homelab/ats/supply/src1'
    name: Homelab voltage source 1
    unit_of_measurement: 'V'
    value_template: "{{ value_json.v }}"
    json_attributes_topic: 'homelab/ats/supply/src1'

  - platform: mqtt
    state_topic: 'homelab/ats/supply/src2'
    name: Homelab voltage source 2
    unit_of_measurement: 'V'
    value_template: "{{ value_json.v }}"
    json_attributes_topic: 'homelab/ats/supply/src2'

  - platform: template
    sensors:
      homelab_preferred:
        friendly_name: 'Homelab preferred source'
        value_template: >-
          {% if states.sensor.homelab_voltage_source_2.attributes['preferred'] == 1 %}
            Secondary
          {% elif states.sensor.homelab_voltage_source_1.attributes['preferred'] == 1 %}
            Primary
          {% else %}
            fail
          {%- endif %}
      homelab_source:
        friendly_name: 'Homelab active source'
        value_template: >-
          {% if states.sensor.homelab_voltage_source_2.attributes['active'] == 1 %}
            Secondary
          {% elif states.sensor.homelab_voltage_source_1.attributes['active'] == 1 %}
            Primary
          {% else %}
            fail
          {%- endif %}


binary_sensor:

  - platform: mqtt
    name: "Homelab source 1 fault"
    state_topic: "homelab/ats/supply/src1"
    value_template: "{{ value_json.bad }}"
    payload_on: "1"
    payload_off: "0"

  - platform: mqtt
    name: "Homelab source 2 fault"
    state_topic: "homelab/ats/supply/src2"
    value_template: "{{ value_json.bad }}"
    payload_on: "1"
    payload_off: "0"
```

### Switches
```yaml
switch:

  - platform: mqtt
    name: "PDU outlet 8"
    command_topic: "homelab/pdu/outlet/out8/set"
    payload_off: 0
    payload_on: 1
```

### Automations
```yml
- alias: Homelab supply fault alert
  hide_entity: False
  trigger:
    - platform: state
      entity_id: binary_sensor.homelab_source_1_fault
      to: 'on'
    - platform: state
      entity_id: binary_sensor.homelab_source_2_fault
      to: 'on'
  action:
    - service: notify.pushover_notify
      data:
        title: "Homelab supply fault"
        message: 'One supply source on homelab has failed!'
        data:
          priority: 2
          timestamp: true
          expire: 3600
          retry: 60
    - service: notify.smtp_notify
      data:
        title: "Homelab supply fault"
        message: 'One supply source on homelab has failed!'
    - service: notify.sms_notify
      data:
        message: 'One supply source on homelab has failed!'
```
