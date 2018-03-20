import powerwalker
import paho.mqtt.publish as publish

# Define PDU and serial port
pdu = powerwalker.PDU("/dev/ttyUSB0")

# Translate responses into more readable topics
topics = {
  'in_w': 'supply',
  'out1_w': 'network',
  'out2_w': 'desktop',
  'out3_w': 'beta',
  'out4_w': 'alpha',
  'out5_w': 'omega',
  'out6_w': 'synology',
  'out7_w': 'peripherals',
  'out8_w': 'aux'
}

# Empty dictionary to hold messages
msgs = []

# Get actual power use in watt
for watt in pdu.power_w().items():
  msg = {
    'topic': 'homelab/power/' + topics[watt[0]],
    'payload': int(watt[1]),
    'qos': 0,
    'retain': False
  }

  msgs.append(msg)

# Publish all messages in dictionary
publish.multiple(msgs, hostname="vm-mqtt")
