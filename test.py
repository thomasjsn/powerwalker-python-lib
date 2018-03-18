import powerwalker

# Define PDU and serial port
pdu = powerwalker.PDU("/dev/ttyUSB0")

# Get info on output #1
watts = pdu.power_watt()

print(watts)
