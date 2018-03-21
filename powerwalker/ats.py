from .pw_common import Powerwalker


class ATS(Powerwalker):
  def __init__(self, port):
    self.port = port
    self.serial = None
    self.connect()


  def connect(self):
    """Connect to ATS device."""
    super().connect()


  def send(self, cmd):
    """Send custom command."""
    return super().send(cmd)


  def info(self):
    """Get and return device information."""
    values = self.send('QRI').split(' ')
    keys = [
      'rated_output_voltage',
      'rated_output_current',
      'battery_voltage',
      'rated_output_freq'
    ]

    params = dict(zip(keys, values))

    return params


  def status(self):
    """Get and return device statuses."""
    values = self.send('QATS').split(' ')
    keys = [
      'src1_voltage',
      'src1_freq',
      'src2_voltage',
      'src2_freq',
      'out_load_pct',
      'out_current',
      'sync_angle',
      'int_temp'
    ]

    params = dict(zip(keys, values))

    params['status'] = self.__status_code()

    return params


  def __status_code(self):
    """Get and return device status code."""
    values = self.send('QAS').split(' ')
    keys = [
      'status'
    ]

    status_keys = [
      'src1_voltage_bad',
      'src1_freq_bad',
      'src1_wave_bad',
      'src2_voltage_bad',
      'src2_freq_bad',
      'src2_wave_bad',
      'on_src2',
      'on_src1',
      'preferred_src2',
      'syncron_bad',
      'aux_pwr1_fail',
      'aux_pwr2_fail',
      'short_fault',
      'overload_fault',
      'overload_alarm',
      'on_fault_mode',
      'na_c7',
      'na_c6',
      'na_c5',
      'na_c4',
      'na_c3',
      'na_c2',
      'na_c1',
      'na_c0'
    ]

    params = super().status_code(values[0], status_keys)

    return params


  def protocol(self):
    """Get and return device protocol ID."""
    return super().protocol()


  def firmware(self):
    """Get and return device firmware version."""
    return super().firmware()


  def memory_get(self, adr):
    """Get and return memory setting at _adr_ location."""
    if int(adr) not in range(0,21):
      raise ValueError('Address must be between 0 and 20')

    mem_keys = [
      'src1_voltage_high_loss',
      'src1_voltage_high_back',
      'src1_voltage_low_loss',
      'src1_voltage_low_back',
      'src1_freq_high_loss',
      'src1_freq_high_back',
      'src1_freq_low_loss',
      'src1_freq_low_high',
      'src2_voltage_high_loss',
      'src2_voltage_high_back',
      'src2_voltage_low_loss',
      'src2_voltage_low_back',
      'src2_freq_high_loss',
      'src2_freq_high_back',
      'src2_freq_low_loss',
      'src2_freq_low_high',
      'overload_alarm',
      'overload_fault',
      'acceptable_phases',
      'breaking_time',
      'blanking_time'
    ]

    idx = '{:04d}'.format(int(adr))

    response = self.send('GM' + idx)

    return { mem_keys[int(adr)]: int(response) }
