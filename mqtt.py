import powerwalker
import paho.mqtt.client as mqtt

# Define PDU and serial port
pdu = powerwalker.PDU("/dev/ttyUSB0")

# Get actual power use in watt
watts = pdu.power_watt()

client = mqtt.Client('powerpi')
client.connect("vm-mqtt", 1883, 60)

for watt in watts.items():
  client.publish('homelab/power/' + watt[0], int(watt[1]))
