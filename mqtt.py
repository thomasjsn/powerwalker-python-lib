import powerwalker
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time
import re
import queue
import config as cfg

# Define devices and serial port
ats = powerwalker.ATS("/dev/ttyUSB0")
pdu = powerwalker.PDU("/dev/ttyUSB1")

pdu_power = {}
pdu_status = {}
ats_status = {}

# Translate responses into more readable topics
topics = {
  'in_w': 'supply',
  'out1_w': 'network',
  'out2_w': 'desktop',
  'out3_w': 'sigma',
  'out4_w': 'alpha',
  'out5_w': 'zeta',
  'out6_w': 'laptop',
  'out7_w': 'peripherals',
  'out8_w': 'aux',
  'src1_voltage': 'src1',
  'src2_voltage': 'src2',
  'out_current': 'current',
  'int_temp': 'temp_c'
}

# Define what status codes from PDU to publish
pdu_fetch = [
  'int_temp'
]

# Define what status codes from ATS to publish
ats_fetch = [
  'src1_voltage',
  'src2_voltage',
  'out_current',
  'int_temp',
  ['on_src1', 'on_src2', 'preferred_src2']
]

# Empty dictionary to hold messages
msgs = []

# Make a queue for holding set commands
q = queue.Queue()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("homelab/outlet/+/+")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    topic_outlet = re.match('homelab\/outlet\/out([1-8])_status\/set', msg.topic)
    if not msg.topic is None:
        idx = topic_outlet.group(1)
        value = bool(int(msg.payload.decode('utf-8')))
        q.put([str(idx), value])


def set_pdu_outlet(idx, value):
    if idx not in ["6"]:
        raise ValueError("Outlet state change not allowed!")

    if value:
        pdu.shutdown_restore(str(idx), "0.1", "0")
    else:
        pdu.shutdown(str(idx), "0.1")


def queue_msg(topic, payload):
  msgs.append({
    'topic': 'homelab/' + topic,
    'payload': payload,
    'qos': 0,
    'retain': False
  })
  print(topic, payload)


# Get actual power use in watt
def get_power_use():
  for watt in pdu_power.items():
    queue_msg('power/' + topics[watt[0]], watt[1])


# Get defined status codes and bits from PDU
def get_pdu_status():
  for i in range(1,9):
    key = 'out' + str(i) + '_status'
    queue_msg('outlet/' + key, pdu_status['status'][key])

  for pdu_status_code in pdu_fetch:

    if isinstance(pdu_status_code, list):
      for pdu_status_bit in pdu_status_code:
        queue_msg('pdu/' + pdu_status_bit, pdu_status['status'][pdu_status_bit])
    else:
      queue_msg('pdu/' + topics[pdu_status_code], pdu_status[pdu_status_code])


# Get defined status codes and bits from ATS
def get_ats_status():
  for ats_status_code in ats_fetch:

    if isinstance(ats_status_code, list):
      for ats_status_bit in ats_status_code:
        queue_msg('ats/' + ats_status_bit, ats_status['status'][ats_status_bit])
    else:
      queue_msg('ats/' + topics[ats_status_code], ats_status[ats_status_code])


# Check source error codes on ATS
def check_supply_sources():
  ats_status_bit = ats_status['status']
  src1_bad = '1' if ats_status_bit['src1_freq_bad'] == 1 or \
		    ats_status_bit['src1_voltage_bad'] == 1 or \
		    ats_status_bit['src1_wave_bad'] == 1 \
		    else '0'
  src2_bad = '1' if ats_status_bit['src2_freq_bad'] == 1 or \
		    ats_status_bit['src2_voltage_bad'] == 1 or \
		    ats_status_bit['src2_wave_bad'] == 1 \
		    else '0'
  queue_msg('ats/src1_bad', src1_bad)
  queue_msg('ats/src2_bad', src2_bad)


client = mqtt.Client('pw_command')
client.username_pw_set(cfg.mqtt['username'], password=cfg.mqtt['password'])

client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.2")
client.loop_start()


while True:
  # Check pending commands and do them
  while not q.empty():
    set_cmd = q.get()
    set_pdu_outlet(set_cmd[0], set_cmd[1])

  # Query modules
  pdu_power = pdu.power_w()
  pdu_status = pdu.status()
  ats_status = ats.status()

  # Parse data
  get_power_use()
  get_pdu_status()
  get_ats_status()
  check_supply_sources()

  # Publish it to MQTT
  publish.multiple(msgs, hostname="192.168.1.2", client_id="pw_status", auth=cfg.mqtt)

  # Rest before doing it again
  time.sleep(5)
