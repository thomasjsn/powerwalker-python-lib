import powerwalker
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Define PDU and serial port, print status
pdu = powerwalker.PDU("/dev/ttyUSB0")
pp.pprint(pdu.power_w())
pp.pprint(pdu.power_va())
