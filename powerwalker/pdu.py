import serial


class PDU:
  def __init__(self, port):
    self.port = port
    self.serial = None
    self.connect()


  def connect(self):
    """Connect to PDU device."""
    self.serial = serial.Serial(
      port=self.port,
      baudrate=2400,
      parity=serial.PARITY_NONE,
      stopbits=serial.STOPBITS_ONE,
      bytesize=serial.EIGHTBITS,
      timeout=1
    )


  def send(self, cmd):
    """Send custom command."""
    self.serial.write(bytes(cmd + '\r', 'utf-8'))
    response = self.serial.readline()

    if response[0] != 40:
      raise ValueError('Response malformed')

    return response[1:].decode('utf-8').rstrip()


  def info(self):
    """Get and return device information."""
    values = self.send('QMD').split(' ')
    keys = [
      'model',
      'in_out_phase',
      'nom_ip_voltage',
      'nom_op_voltage',
      'in_socket_no',
      'out_socket_no'
    ]

    params = dict(zip(keys, values))

    return params


  def status(self):
    """Get and return device statuses."""
    values = self.send('QGS').split(' ')
    keys = [
      'status',
      'in_voltage',
      'in_freq',
      'in_current',
      'out1_current',
      'out2_current',
      'out3_current',
      'out4_current',
      'out5_current',
      'out6_current',
      'out7_current',
      'out8_current',
      'temp'
    ]

    params = dict(zip(keys, values))

    return params


  def power_watt(self):
    """Get and return active power measurements."""
    values = self.send('QPW').split(' ')
    keys = [
      'in_power',
      'out1_power',
      'out2_power',
      'out3_power',
      'out4_power',
      'out5_power',
      'out6_power',
      'out7_power',
      'out8_power',
    ]

    params = dict(zip(keys, values))

    return params


  def power_va(self):
    """Get and return apparent power measurements."""
    values = self.send('QPVA').split(' ')
    keys = [
      'in_power',
      'out1_power',
      'out2_power',
      'out3_power',
      'out4_power',
      'out5_power',
      'out6_power',
      'out7_power',
      'out8_power',
    ]

    params = dict(zip(keys, values))

    return params


  def test(self):
    """Test PDU device, turn on all LEDs and the buzzer for 5 seconds."""
    response = self.send('TP')

    return response
