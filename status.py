import powerwalker
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Define PDU and serial port, print status
pdu = powerwalker.PDU("/dev/ttyUSB0")
pp.pprint(pdu.status())

# Define ATS and serial port, print status
ats = powerwalker.ATS("/dev/ttyUSB1")
pp.pprint(ats.status())
