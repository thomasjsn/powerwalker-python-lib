import powerwalker
import paho.mqtt.publish as publish
import time

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
  'out3_w': 'beta',
  'out4_w': 'alpha',
  'out5_w': 'omega',
  'out6_w': 'synology',
  'out7_w': 'peripherals',
  'out8_w': 'aux',
  'src1_voltage': 'src1',
  'src2_voltage': 'src2'
}

# Define what status codes from ATS to publish
ats_fetch = [
  'src1_voltage',
  'src2_voltage',
  ['on_src1', 'on_src2', 'preferred_src2']
]

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


# Get actual power use in watt
def get_power_use():
  for watt in pdu_power.items():
    queue_msg('power/' + topics[watt[0]], int(watt[1]))


# Get defined status codes and bits from PDU
def get_pdu_status():
  for i in range(1,9):
    key = 'out' + str(i) + '_status'
    queue_msg('outlet/' + key, pdu_status['status'][key])


# Get defined status codes and bits from ATS
def get_ats_status():
  for ats_status_code in ats_fetch:

    if isinstance(ats_status_code, list):
      for ats_status_bit in ats_status_code:
        queue_msg('voltage/' + ats_status_bit, ats_status['status'][ats_status_bit])
    else:
      queue_msg('voltage/' + topics[ats_status_code], float(ats_status[ats_status_code]))


# Check source error codes on ATS
def check_supply_sources():
  ats_status_bit = ats_status['status']
  src1_bad = '1' if ats_status_bit['src1_freq_bad'] == '1' or \
		    ats_status_bit['src1_voltage_bad'] == '1' or \
		    ats_status_bit['src1_wave_bad'] == '1' \
		    else '0'
  src2_bad = '1' if ats_status_bit['src2_freq_bad'] == '1' or \
		    ats_status_bit['src2_voltage_bad'] == '1' or \
		    ats_status_bit['src2_wave_bad'] == '1' \
		    else '0'
  queue_msg('voltage/src1_bad', src1_bad)
  queue_msg('voltage/src2_bad', src2_bad)


while True:
  pdu_power = pdu.power_w()
  pdu_status = pdu.status()
  ats_status = ats.status()

  get_power_use()
  get_pdu_status()
  get_ats_status()
  check_supply_sources()

  publish.multiple(msgs, hostname="vm-mqtt")

  time.sleep(20)
