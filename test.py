import powerwalker

# Define PDU and serial port
pdu = powerwalker.PDU("/dev/ttyUSB0")

# Get actual power use in watt
watts = pdu.power_watt()

print(watts)
