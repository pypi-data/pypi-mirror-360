# Author: Chris Braissant
#
# Driver for the ST LPS22HH:
# High-performance MEMS nano pressure sensor:
# 260-1260 hPa absolute digital output barometer

from machine import SPI, I2C, Pin
from .register import Register, Bits

_INTERRUPT_CFG = 0x0B
_THS_P_L = 0x0C
_THS_P_H = 0x0D
_IF_CTRL = 0x0E
_WHO_AM_I = 0x0F
_CTRL_REG1 = 0x10
_CTRL_REG2 = 0x11
_CTRL_REG3 = 0x12
_FIFO_CTRL = 0x13
_FIFO_WTM = 0x14
_REF_P_L = 0x15
_REF_P_H = 0x16
_RPDS_L = 0x18
_RPDS_H = 0x19
_INT_SOURCE = 0x24
_FIFO_STATUS1 = 0x25
_FIFO_STATUS2 = 0x26
_STATUS = 0x27
_PRESS_OUT_XL = 0x28
_PRESS_OUT_L = 0x29
_PRESS_OUT_H = 0x2A
_TEMP_OUT_L = 0x2B
_TEMP_OUT_H = 0x2C
_FIFO_DATA_OUT_PRESS_XL = 0x78
_FIFO_DATA_OUT_PRESS_L = 0x79
_FIFO_DATA_OUT_PRESS_H = 0x7A
_FIFO_DATA_OUT_TEMP_L = 0x7B
_FIFO_DATA_OUT_TEMP_H = 0x7C

_PRESSURE_SENSITIVITY = 4096       # 4096 LSB = 1 hPa
_PRESSURE_RESOLUTION = 0.00024414  # 1 LSB = 1/4096 = 0.0002441406 hPa
_TEMPERATURE_SENSITIVITY = 100     # 100 LSB = °C
_TEMPERATURE_RESOLUTION =  0.01    # 1 LSB = 1/100 = 0.01 °C

_HPA_TO_MMHG = 0.75006157          # 1 hPa = 0.75006157 mmHg

_ODR_MAP = {
    0: 0,   # One-shot mode
    1: 1,   # 1 Hz
    2: 10,  # 10 Hz
    3: 25,  # 25 Hz
    4: 50,  # 50 Hz
    5: 75,  # 75 Hz
    6: 100, # 100 Hz
    7: 200, # 200 Hz
}


class LPS22HH:

    # REGISTERS
    _interrupt_cfg = Register(_INTERRUPT_CFG, 1)
    _ths_p = Register(_THS_P_L, 2)
    _if_ctrl = Register(_IF_CTRL, 1)
    _who_am_i = Register(_WHO_AM_I, 1)
    _ctrl_reg1 = Register(_CTRL_REG1, 1)
    _ctrl_reg2 = Register(_CTRL_REG2, 1)
    _ctrl_reg3 = Register(_CTRL_REG3, 1)
    _fifo_ctrl = Register(_FIFO_CTRL, 1)
    _fifo_wtm = Register(_FIFO_WTM, 1)
    _ref_p = Register(_REF_P_L, 2)
    _rpds = Register(_RPDS_L, 2)
    _int_source = Register(_INT_SOURCE, 1)
    _fifo_status1 = Register(_FIFO_STATUS1, 1)
    _fifo_status2 = Register(_FIFO_STATUS2, 1)
    _status = Register(_STATUS, 1)
    _press_out = Register(_PRESS_OUT_XL, 3)
    _temp_out = Register(_TEMP_OUT_L, 2)
    _fifo_data_out_press = Register(_FIFO_DATA_OUT_PRESS_XL, 3)
    _fifo_data_out_temp = Register(_FIFO_DATA_OUT_TEMP_L, 2)
    
    # INTERRUPT_CFG
    _autorefp = Bits(_INTERRUPT_CFG, 7, 1)
    _reset_arp = Bits(_INTERRUPT_CFG, 6, 1)
    _autozero = Bits(_INTERRUPT_CFG, 5, 1)
    _reset_az = Bits(_INTERRUPT_CFG, 4, 1)
    _diff_en = Bits(_INTERRUPT_CFG, 3, 1)
    _lir = Bits(_INTERRUPT_CFG, 2, 1)
    _ple = Bits(_INTERRUPT_CFG, 1, 1)
    _phe = Bits(_INTERRUPT_CFG, 0, 1)

    # IF_CTRL
    _int_en_i3c = Bits(_IF_CTRL, 7, 1)
    _sda_pu_en = Bits(_IF_CTRL, 4, 1)
    _sdo_pu_en = Bits(_IF_CTRL, 3, 1)
    _pd_dis_int1 = Bits(_IF_CTRL, 2, 1)
    _i3c_disable = Bits(_IF_CTRL, 1, 1)
    _i2c_disable = Bits(_IF_CTRL, 0, 1)

    # CTRL_REG1
    _odr = Bits(_CTRL_REG1, 4, 3)
    _en_lpfp = Bits(_CTRL_REG1, 3, 1)
    _lpfp_cfg = Bits(_CTRL_REG1, 2, 1)
    _bdu = Bits(_CTRL_REG1, 1, 1)
    _sim = Bits(_CTRL_REG1, 0, 1)

    # CTRL_REG2
    _boot = Bits(_CTRL_REG2, 7, 1)
    _int_h_l = Bits(_CTRL_REG2, 6, 1)
    _pp_od = Bits(_CTRL_REG2, 5, 1)
    _if_add_inc = Bits(_CTRL_REG2, 4, 1)
    _swreset = Bits(_CTRL_REG2, 2, 1)
    _low_noise_en = Bits(_CTRL_REG2, 1, 1)
    _one_shot = Bits(_CTRL_REG2, 0, 1)

    # CTRL_REG3
    _int_f_full = Bits(_CTRL_REG3, 5, 1)
    _int_f_wtm = Bits(_CTRL_REG3, 4, 1)
    _int_f_ovr = Bits(_CTRL_REG3, 3, 1)
    _drdy = Bits(_CTRL_REG3, 2, 1)
    _int_s1 = Bits(_CTRL_REG3, 1, 1)
    _int_s0 = Bits(_CTRL_REG3, 0, 1)

    # FIFO_CTRL
    _stop_on_wtm = Bits(_FIFO_CTRL, 3, 1)
    _trig_modes = Bits(_FIFO_CTRL, 2, 1)
    _f_mode1 = Bits(_FIFO_CTRL, 1, 1)
    _f_mode0 = Bits(_FIFO_CTRL, 0, 1)

    # INT_SOURCE
    _boot_on = Bits(_INT_SOURCE, 7, 1)
    _ia = Bits(_INT_SOURCE, 2, 1)
    _pl = Bits(_INT_SOURCE, 1, 1)
    _ph = Bits(_INT_SOURCE, 0, 1)

    # FIFO_STATUS2
    _fifo_wtm_ia = Bits(_FIFO_STATUS2, 7, 1)
    _fifo_ovr_ia = Bits(_FIFO_STATUS2, 6, 1)
    _fifo_full_ia = Bits(_FIFO_STATUS2, 5, 1)

    # STATUS
    _t_or = Bits(_STATUS, 5, 1)
    _p_or = Bits(_STATUS, 4, 1)
    _t_da = Bits(_STATUS, 1, 1)
    _p_da = Bits(_STATUS, 0, 1)
    

    def __init__(self, interface, cs=None, address=0x5D):
        """
        Initialize with either SPI or I2C interface.
        For SPI: provide `interface=SPI(...)`, `cs=Pin(...)`
        For I2C: provide `interface=I2C(...)`, `address=<i2c address>`
        """
        if isinstance(interface, SPI):
            self.spi = interface
            self.cs = cs
        elif isinstance(interface, I2C):
            self.i2c = interface
            self.i2c_addr = address
        else:
            raise TypeError("Interface must be an instance of machine.SPI or machine.I2C")


    def reset(self):
        """
        Reset the volatile registers to their default value  
        The following registers are reset to their default value:
        INTERRUPT_CFG, THS_P_L, THS_P_H, IF_CTRL, CTRL_REG1, CTRL_REG2, CTRL_REG3
        FIFO_CTRL, FIFO_WTM, INT_SOURCE, FIFO_STATUS1, FIFO_STATUS2, STATUS
        """
        self._swreset = 1
        while self._swreset:
            pass


    def boot(self):
        """
        Reboots memory content and reload trimming parameters.
        Used to refresh the content of the internal registers stored in the flash.
        The following registers are reset to their default value:
        RPDS_L, RPDS_H
        """
        self._boot = 1
        while self._boot_on:
            pass


    @property
    def device_id(self):
        """
        Device identification
        Return the value of the who_am_i register.
        For the LPS22HH, the value is 179 (0xB3)
        """
        return self._who_am_i


    @property
    def raw_pressure(self):
        """
        Pressure value as a 24-bit data.
        The output pressure is provided as the difference between the
        measured pressure and the content of the pressure offset register RPDS
        The value is expressed as 2's complement.
        """
        return self._press_out


    @property
    def pressure(self):
        """
        Pressure in [hPa]
        """
        return self._press_out * _PRESSURE_RESOLUTION


    @property
    def pressure_in_mmhg(self):
        """
        Pressure in [mmHg]
        """
        return self.pressure * _HPA_TO_MMHG


    @property
    def raw_temperature(self):
        """
        Temperature value as a 16-bit data.
        The value is expressed as 2's complement.
        """
        return self._temp_out
    

    @property
    def temperature(self):
        """
        Temperature in [°C]
        """
        return self._temp_out * _TEMPERATURE_RESOLUTION
    

    @property
    def temperature_in_kelvin(self):
        """
        Temperature in [K]
        """
        return self.temperature + 273.15
    

    @property
    def temperature_in_farenheit(self):
        """
        Temperature in [°F]
        """
        return (self.temperature * 9/5) + 32
    

    @property
    def reference_pressure(self):
        """
        Reference pressure value as a 16-bit data
        User-defined value used as a baseline for pressure measurements.
        Establish a reference point for pressure measurements and calculate
        the pressure relative to this reference
        """
        return self._ref_p


    @reference_pressure.setter
    def reference_pressure(self, data):
        self._ref_p = data
    

    @property
    def pressure_offset(self):
        """
        Pressure offset as a 16-bit data.
        The pressure offset value can be used to implement one-point
        calibration (OPC) after soldering.
        The content of the RPDS registers is always automatically subtracted
        from the compensated pressure output and provided to the standard
        output pressure registers.
        It is provided as the difference between the measured pressure and
        the content of the RPDS registers multiplied by 256 (AN5387)
        The value is expressed as 2's complement.
        """
        return self._rpds


    @pressure_offset.setter
    def pressure_offset(self, data):
        self._rpds = data


    @property
    def data_rate(self):
        """
        Output data rate (ODR) selection
        When the ODR is set to 0, the device is in Power-down mode and the
        content of the output data registers are not updated.
        When the ODR bits are set to a value different than 0, the device is
        in Continuous mode and automatically acquires a set of data
        (pressure and temperature) at the frequency selected.
        """
        # Default to one-shot mode (0) if _odr value not found
        return _ODR_MAP.get(self._odr, 0)
    

    @data_rate.setter
    def data_rate(self, data_rate):
        for value, frequency in _ODR_MAP.items():
            if data_rate <= frequency:
                self._odr = value
                break


    @property
    def new_pressure_data(self):
        """
        New pressure sample available in the output registers
        Self cleared when the pressure sample is read
        """
        return self._p_da


    @property
    def new_temperature_data(self):
        """
        New temperature sample available in the output registers
        Self cleared when the temperature sample is read
        """
        return self._t_da
    

    def trigger_measurement(self):
        """
        Triggers a single measurement of pressure and temperature.
        Once the measurement is done, the bit will self-clear.
        """
        self._one_shot = 1


    @property
    def fifo_watermark(self):
        """
        FIFO watermark level, in number of samples
        Used to indicate that the FIFO has reached a certain fill level
        and generate interrupt
        """
        return self._fifo_wtm


    @fifo_watermark.setter    
    def fifo_watermark(self, data):
        self._fifo_wtm = data
    

    @property
    def low_noise_enable(self):
        """
        Select between low-current and low-noise.
        • When set to '0', low-current mode is selected (default configuration);
        • When set to '1', low-noise mode is selected
        If ODR = 100 Hz or ODR = 200 Hz, this option is automatically switched
        off and the value of the low-noise enable bit is ignored.
        Note: For proper behavior of the pressure sensor, the mode must be
        changed only when the device is in power-down mode (ODR = 0).
        """
        return self._low_noise_en
    

    @low_noise_enable.setter
    def low_noise_enable(self, data):
        # TODO Power down before changing mode
        self._low_noise_en = data


    @property
    def low_pass_filter_enable(self):
        """
        Enables the low pass filter and diverts its output to the pressure
        output registers and FIFO buffer.
        The filter is reset if the data rate or the filter bandwidth change.
        """
        return self._en_lpfp


    @low_pass_filter_enable.setter
    def low_pass_filter_enable(self, data):
        self._en_lpfp = data
  

    @property
    def low_pass_filter_configuration(self):
        """
        Configure the device bandwidth for the low-pass filter
        """
        return self._lpfp_cfg
    

    @low_pass_filter_configuration.setter
    def low_pass_filter_configuration(self, data):
        self._lpfp_cfg = data


    @property
    def block_data_update(self):
        """
        BDU is used to inhibit the update of the output registers until all
        output registers parts are read, to avoids reading values from
        different sample times
        0: Values updated continuously.
        1: Values not updated until MSB, LSB and XLSB have been read
        """
        return self._bdu
    

    @block_data_update.setter
    def block_data_update(self, data):
        self._bdu = data
