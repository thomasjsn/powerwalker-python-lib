import powerwalker
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)

# Define PDU and serial port, print status
pdu = powerwalker.PDU("/dev/ttyUSB0")
ats = powerwalker.ATS("/dev/ttyUSB1")

if len(sys.argv) < 3:
  raise ValueError('Missing arguments.')

if sys.argv[1] != 'ats' and sys.argv[1] != 'pdu':
  raise ValueError('First argument must be "ats" or "pdu".')

if sys.argv[1] == 'ats':
  device = ats
elif sys.argv[1] == 'pdu':
  device = pdu

method = getattr(device, sys.argv[2])

# Remove first three items from list, use rest as method arguments
args = sys.argv
args.pop(0)
args.pop(0)
args.pop(0)

if len(args) == 0:
  response = method()
else:
  response = method(*args)

pp.pprint(response)
