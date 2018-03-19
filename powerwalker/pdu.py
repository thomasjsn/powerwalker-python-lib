import serial
from .pw_common import Powerwalker


class PDU(Powerwalker):
  def __init__(self, port):
    self.port = port
    self.serial = None
    self.connect()


  def connect(self):
    """Connect to PDU device."""
    super().connect()


  def send(self, cmd):
    """Send custom command."""
    return super().send(cmd)


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

    status_keys = [
      'a01_low_in_voltage',
      'a02_high_in_voltage',
      'f09_low_in_current',
      'f10_high_in_current',
      'f11_pwr_fail_aux1',
      'f12_pwr_fail_aux2',
      'b9_na',
      'b8_na',
      'out1_status',
      'out2_status',
      'out3_status',
      'out4_status',
      'out5_status',
      'out6_status',
      'out7_status',
      'out8_status'
    ]

    params = dict(zip(keys, values))

    params['status'] = super().status_code(values[0], status_keys)

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
