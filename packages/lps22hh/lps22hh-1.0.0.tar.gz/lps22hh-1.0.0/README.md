# LPS22HH Pico Driver
Micropython library for the ST LPS22HH and the LPS27HH pressure sensor over SPI or I2C

## Overview
The LPS22HH and LPS27HH sensors are high-resolution digital output pressure sensors manufactured by STMicroelectronics.
This driver enables seamless integration of the sensors with the Raspberry Pi Pico.

## Features
- Interface to communicate with the LPS22HH and LPS27HH pressure sensor.
- Reading of pressure and temperature values
- Configuration of registers via dedicated functions
- Communication via SPI or I2C
- Designed to be compatible with the Raspberry Pi Pico running on Micropython. Other boards not tested

## Installation
Use `pip` (see [Python Package Index ](https://pypi.org/))

```bash
> pip install lps22hh
```

or 

Use `mip` (see MicroPython [Package management](https://docs.micropython.org/en/latest/reference/packages.html)):

```bash
> mpremote mip install github:cbraissant/lps22hh-pico-driver
```

## Getting Started

As the sensor can be used either with SPI or I2C, the first step is to initialize the interface.

For SPI:
```python
from machine import SPI, Pin
from lps22hh import LPS22HH

# Create a new SPI device, and assign the pins corresponding to your device
cs_pin = Pin(1, Pin.OUT)
spi = SPI(0, baudrate=1000000, firstbit=SPI.MSB, sck=Pin(2), mosi=Pin(3), miso=Pin(0))

# Create a new instance of the LPS22HH sensor
sensor = LPS22HH(spi, cs_pin)
```

For I2C:
```python
import time
from machine import I2C, Pin
from lps22hh import LPS22HH

# Create a new I2C device, and assign the pins corresponding to your device
i2c = I2C(1, sda=Pin(6), scl=Pin(7))

# Create a new instance of the Lps22hh sensor
sensor = LPS22HH(interface=i2c, address=0x5D)
```

And then interact with the device

```python
# By default, the device is in power-down mode and the ODR need to be changed
# for the device to take continuous measurements
sensor.data_rate = 200

# The Block Data Update (BDU) is used to inhibit the update of the output
# registers until all output registers parts are read, to avoids reading values
# from different sample times
sensor.block_data_update = 1

while True:
    if sensor.new_pressure_data:
        print(sensor.pressure)
```

## Remarks
Some microcontrollers, like the RP2040 start faster than the pressure sensor.
To make sure the sensor has time to boot, a delay must be introduced before the definition of the instance.
```python
...
from lps22hh import LPS22HH

# The RP2040 starts faster than the LPSxxHH pressure sensor and a delay must be introduced
time.sleep_ms(100)

# Create a new I2C device, and assign the pins corresponding to your device
i2c = I2C(1, sda=Pin(6), scl=Pin(7))
...
```
See the [I2C](./example/i2c_read_sensor.py) or [SPI](/example/spi_read_sensor.py) examples for the full code.

## TODO
- [ ] FIFO functionalities
- [ ] Interrupts
- [ ] I3C communications

## Contributing
Contributions to this project are welcome. If you find any issues, have suggestions for improvements, or want to add new features, feel free to open an issue or submit a pull request.

## License
This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code in accordance with the terms of the license.
