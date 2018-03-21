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
      'nom_in_voltage',
      'nom_out_voltage',
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
      'int_temp'
    ]

    status_keys = [
      'a01_low_in_voltage',
      'a02_high_in_voltage',
      'f09_low_in_current',
      'f10_high_in_current',
      'f11_pwr_fail_aux1',
      'f12_pwr_fail_aux2',
      'na_b9',
      'na_b8',
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


  def power_w(self):
    """Get and return active power (W) measurements for input and all outputs."""
    values = self.send('QPW').split(' ')
    keys = [
      'in_w',
      'out1_w',
      'out2_w',
      'out3_w',
      'out4_w',
      'out5_w',
      'out6_w',
      'out7_w',
      'out8_w',
    ]

    params = dict(zip(keys, values))

    return params


  def power_va(self):
    """Get and return apparent power (VA) measurements for input and all outputs."""
    values = self.send('QPVA').split(' ')
    keys = [
      'in_va',
      'out1_va',
      'out2_va',
      'out3_va',
      'out4_va',
      'out5_va',
      'out6_va',
      'out7_va',
      'out8_va',
    ]

    params = dict(zip(keys, values))

    return params


  def energy_kwh(self):
    """Get and return energy consumption (kWh) for input and all outputs."""
    values = self.send('QEC').split(' ')
    keys = [
      'in_kwh',
      'out1_kwh',
      'out2_kwh',
      'out3_kwh',
      'out4_kwh',
      'out5_kwh',
      'out6_kwh',
      'out7_kwh',
      'out8_kwh',
    ]

    params = dict(zip(keys, values))

    return params


  def energy_kwh_clear(self):
    """Clear energy consumption values for input and all outputs."""
    response = self.send('CEC')

    return response


  def countdown_times(self):
    """Get and return shutdown and restore countdown times for all outputs."""
    values = self.send('QSR').split(' ')

    triplets = {}

    for x in range(0, 8):
      idx = x * 3
      triplets['out' + str(x+1) + '_cd_sec'] = {'s': values[idx+1][0:4], 'r': (values[idx+2][0:6])}

    return triplets


  def shutdown(self, idx, shdn):
    """Shutdown output _idx_ in _shdn_ minutes.

    Arguments:
    idx  : output; 1 to 8, A for all
    shdn : shutdown delay in minutes; .1 to .9, 01 to 99, 00 for immediate
    """
    response = self.send('S,' + idx + shdn)

    return response


  def shutdown_restore(self, idx, shdn, rst):
    """Shutdown output _idx_ in _shdn_ minutes, restore power after _rst_ minutes.

    Arguments:
    idx  : output; 1 to 8, A for all
    shdn : shutdown delay in minutes; .1 to .9, 01 to 99, 00 for immediate
    rst  : restore delay in minutes; 0000 to 9999, 0000 for 1 second
    """
    response = self.send('S,' + idx + shdn + 'R' + rst)

    return response


  def shutdown_cancel(self, idx):
    """Cancel pending shutdown on output _idx_.

    Arguments:
    idx  : output; 1 to 8, A for all
    """
    response = self.send('CS,' + idx)

    return response


  def protocol(self):
    """Get and return device protocol ID."""
    return super().protocol()


  def firmware(self):
    """Get and return device firmware version."""
    return super().firmware()


  def test(self):
    """Test PDU device, turn on all LEDs and the buzzer for 5 seconds."""
    response = self.send('TP')

    return response


  def memory_get(self, adr):
    """Get and return memory setting at _adr_ location."""
    if int(adr) not in range(0,15):
      raise ValueError('Address must be between 0 and 14')

    mem_map = ['00','01','02','03','04','05','06','07','08','09','0:','0;','0<','0=','0>','0?']

    mem_keys = [
      'output_start_up_delay',
      { 'low': 'out1_current_alarm', 'high': 'out1_config' },
      { 'low': 'out2_current_alarm', 'high': 'out2_config' },
      { 'low': 'out3_current_alarm', 'high': 'out3_config' },
      { 'low': 'out4_current_alarm', 'high': 'out4_config' },
      { 'low': 'out5_current_alarm', 'high': 'out5_config' },
      { 'low': 'out6_current_alarm', 'high': 'out6_config' },
      { 'low': 'out7_current_alarm', 'high': 'out7_config' },
      { 'low': 'out8_current_alarm', 'high': 'out8_config' },
      'low_input_voltage_alarm',
      'high_input_voltage_alarm',
      'max_input_voltage_shutoff',
      'low_input_current_alarm',
      'high_input_current_alarm',
      'shutdown_imminent_signal',
    ]

    response = self.send('QGM' + mem_map[int(adr)])

    response = response.replace(':','A').replace(';','B').replace('<','C').replace('=','D').replace('>','E').replace('?','F')

    if isinstance(mem_keys[int(adr)], dict):
      mem_value = {
	mem_keys[int(adr)]['high']: int(response[2:4], 16),
	mem_keys[int(adr)]['low']: int(response[4:6], 16)
      }
    else:
      mem_value = {
	mem_keys[int(adr)]: int(response[2:6], 16)
      }

    return mem_value
