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

    return params


  def status(self):
    """Get and return device statuses."""
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
      'src2_preferred',
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

    params = dict(zip(keys, values))

    params['status'] = super().status_code(values[0], status_keys)

    return params
