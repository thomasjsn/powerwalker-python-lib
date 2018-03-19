import powerwalker
import paho.mqtt.publish as publish

# Define PDU and serial port
pdu = powerwalker.PDU("/dev/ttyUSB0")

# Get actual power use in watt
watts = pdu.power_watt()

msgs = []

for watt in watts.items():
  msg = {
    'topic': 'homelab/power/' + watt[0],
    'payload': int(watt[1]),
    'qos': 0,
    'retain': False
  }

  msgs.append(msg)

publish.multiple(msgs, hostname="vm-mqtt")
