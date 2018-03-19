import powerwalker
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Define PDU and serial port, print info
pdu = powerwalker.PDU("/dev/ttyUSB0")
pp.pprint(pdu.info())

# Define ATS and serial port, print info
ats = powerwalker.ATS("/dev/ttyUSB1")
pp.pprint(ats.info())
