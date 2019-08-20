import powerwalker
import paho.mqtt.client as mqtt
import time
import re
import queue
import config as cfg
import json

# Define devices and serial port
ats = powerwalker.ATS(cfg.port['ats'])
pdu = powerwalker.PDU(cfg.port['pdu'])

pdu_status = {}
pdu_countdown = {}
ats_status = {}
pdu_power_w = {}
pdu_power_va = {}

# All states an outlet can have
pdu_outlet_states = [
  'Off',
  'On',
  'Shutdown active',
  'Shutdown imminent',
  'Restore active',
  'Overload alarm',
  'Locked'
]

# Queue for messages to be published
msgs = queue.Queue()

# Queue for holding set commands
q = queue.Queue()

# Dict for alers
alerts = {}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(cfg.mqtt['prefix'] + "/pdu/outlet/+/+")

    if rc==0:
        client.connected_flag=True
        client.publish("$CONNECTED/" + cfg.mqtt['client_id'], 1, retain=True)
    else:
        client.bad_connection_flag=True


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    topic_outlet = re.match(cfg.mqtt['prefix'] + '\/pdu\/outlet\/out([1-8])\/set', msg.topic)
    if not msg.topic is None:
        idx = topic_outlet.group(1)
        value = bool(int(msg.payload.decode('utf-8')))
        q.put([str(idx), value])


def set_pdu_outlet(idx, value):
    if idx not in cfg.allow_state_change:
        raise ValueError("Outlet state change not allowed!")

    if value:
        pdu.shutdown_restore(str(idx), "0.1", "0")
    else:
        pdu.shutdown(str(idx), "0.1")


def queue_msg(topic, payload):
  msgs.put({
    'topic': cfg.mqtt['prefix'] + '/' + topic,
    'payload': payload,
    'qos': 0,
    'retain': False
  })
  print(topic, payload)


# Get actual power use in watt
def get_power_use():
  for watt in pdu_power_w.items():
    key = watt[0][:-2]

    data = {
      'w': watt[1],
      'va': pdu_power_va[key + '_va'],
      'a': pdu_status[key + '_current']
    }

    queue_msg('pdu/power/' + key, json.dumps(data))


# Get defined status codes and bits from PDU
def get_pdu_status():
  for i in range(1,9):
    key = 'out' + str(i)

    data = {
      'status': pdu_status['status'][key + '_status'],
      'state':  pdu_outlet_states[pdu_status['status'][key + '_status']],
      'restore_sec': pdu_countdown[key + '_cd_sec']['r'],
      'shutdown_sec': pdu_countdown[key + '_cd_sec']['s']
    }

    queue_msg('pdu/outlet/' + key, json.dumps(data))
    alerts['pdu_' + key] = int(pdu_status['status'][key + '_status'] == 5)

  status_data = {
    'in_hz': pdu_status['in_freq'],
    'in_v': pdu_status['in_voltage'],
    'temp_c': pdu_status['int_temp'],
    'low_in_voltage': pdu_status['status']['a01_low_in_voltage'],
    'high_in_voltage': pdu_status['status']['a02_high_in_voltage'],
    'low_in_current': pdu_status['status']['f09_low_in_current'],
    'high_in_current': pdu_status['status']['f10_high_in_current'],
    'pwr_fail_aux1': pdu_status['status']['f11_pwr_fail_aux1'],
    'pwr_fail_aux2': pdu_status['status']['f12_pwr_fail_aux2']
  }

  queue_msg('pdu/status', json.dumps(status_data))

  alert = 1 if pdu_status['status']['a01_low_in_voltage'] == 1 or \
               pdu_status['status']['a02_high_in_voltage'] == 1 or \
               pdu_status['status']['f09_low_in_current'] == 1 or \
               pdu_status['status']['f10_high_in_current'] == 1 or \
               pdu_status['status']['f11_pwr_fail_aux1'] == 1 or \
               pdu_status['status']['f12_pwr_fail_aux2'] == 1 \
               else 0

  alerts['pdu'] = alert


# Get defined status codes and bits from ATS
def get_ats_status():
  for i in range(1,3):
    key = 'src' + str(i)
    preferred = 'src2' if ats_status['status']['preferred_src2'] == 1 else 'src1'

    ats_status_bit = ats_status['status']
    bad = 1 if ats_status_bit[key + '_freq_bad'] == 1 or \
	       ats_status_bit[key + '_voltage_bad'] == 1 or \
	       ats_status_bit[key + '_wave_bad'] == 1 \
	       else 0

    alerts['ats_' + key] = bad

    data = {
      'v': ats_status[key + '_voltage'],
      'hz': ats_status[key + '_freq'],
      'active': ats_status['status']['on_' + key],
      'preferred': 1 if preferred == key else 0,
      'bad': bad
    }

    queue_msg('ats/supply/' + key, json.dumps(data))

  status_data = {
    'temp_c': ats_status['int_temp'],
    'out_a': ats_status['out_current'],
    'out_pct':  ats_status['out_load_pct'],
    'sync_angle': ats_status['sync_angle'],
    'aux_pwr1_fail': ats_status['status']['aux_pwr1_fail'],
    'aux_pwr2_fail': ats_status['status']['aux_pwr2_fail'],
    'on_fault_mode': ats_status['status']['on_fault_mode'],
    'overload_alarm': ats_status['status']['overload_alarm'],
    'overload_fault': ats_status['status']['overload_fault'],
    'short_fault': ats_status['status']['short_fault'],
    'syncron_bad': ats_status['status']['syncron_bad']
  }

  queue_msg('ats/status', json.dumps(status_data))

  alert = 1 if ats_status['status']['aux_pwr1_fail'] == 1 or \
               ats_status['status']['aux_pwr2_fail'] == 1 or \
               ats_status['status']['on_fault_mode'] == 1 or \
               ats_status['status']['overload_alarm'] == 1 or \
               ats_status['status']['overload_fault'] == 1 or \
               ats_status['status']['short_fault'] == 1 or \
               ats_status['status']['syncron_bad'] == 1 \
               else 0

  alerts['ats'] = alert


client = mqtt.Client(cfg.mqtt['client_id'])
client.username_pw_set(cfg.mqtt['auth']['username'], password=cfg.mqtt['auth']['password'])

client.on_connect = on_connect
client.on_message = on_message
client.will_set("$CONNECTED/" + cfg.mqtt['client_id'], 0, qos=0, retain=True)
client.connect(cfg.mqtt['host'])
client.loop_start()


while True:
  # Check pending commands and do them
  while not q.empty():
    set_cmd = q.get()
    set_pdu_outlet(set_cmd[0], set_cmd[1])

  # Query PDU
  pdu_status = pdu.status()
  pdu_countdown = pdu.countdown_times()
  pdu_power_w = pdu.power_w()
  pdu_power_va = pdu.power_va()

  # Parse data from PDU
  get_pdu_status()
  get_power_use()

  # Query ATS
  ats_status = ats.status()

  # Parse data from ATS
  get_ats_status()

  # Queue alerts as json string
  queue_msg('alert', json.dumps(alerts))

  # Publish it to MQTT
  while not msgs.empty():
      client.publish(**msgs.get())

  print('--- End of loop ---')
