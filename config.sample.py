# Sample configuration file for the mqtt.py/ups.py scripts

port = {
  'ats': "/dev/ttyUSB0",
  'pdu': "/dev/ttyUSB1"
}

mqtt = {
  'host': '192.168.1.2',
  'client_id': 'powerwalker',
  'auth': {'username':"powerwalker", 'password':"powerwalker"},
  'prefix': 'powerwalker'
}

allow_state_change = ["1", "2", "3", "4", "5", "6", "7", "8"]
