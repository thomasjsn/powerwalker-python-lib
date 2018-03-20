import powerwalker
import pprint

pp = pprint.PrettyPrinter(indent=4)

# Define PDU and serial port, print status
pdu = powerwalker.PDU("/dev/ttyUSB0")
pp.pprint(pdu.power_watt())
pp.pprint(pdu.power_va())
pp.pprint(pdu.power_kwh())
