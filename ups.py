import paho.mqtt.publish as publish
import time
import subprocess


# Empty dictionary to hold messages
msgs = []


def queue_msg(topic, payload):
  msgs.append({
    'topic': 'homelab/' + topic,
    'payload': payload,
    'qos': 0,
    'retain': False
  })
  print(topic, payload)


while True:
  result = subprocess.run(['upsc', 'ups'], stdout=subprocess.PIPE)
  
  result_list = result.stdout.decode('utf-8').split("\n")

  result_dict = {}

  for line in result_list:
      segments = line.split(":")

      if line:
          result_dict[segments[0]] = segments[1]

  to_send = [
    "battery.charge",
    "battery.runtime",
    "battery.voltage",
    "ups.load",
    "ups.status"
  ]

  for value_to_send in to_send:
      queue_msg("ups/" + value_to_send, result_dict[value_to_send])

  publish.multiple(msgs, hostname="vm-mqtt")

  time.sleep(10)
