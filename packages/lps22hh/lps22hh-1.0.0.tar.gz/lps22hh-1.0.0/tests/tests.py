from machine import SPI, Pin
from time import sleep
from tests.unittest import Test, bcolors
from lps22hh import LPS22HH

def test_basic():
    print(f'{bcolors.BOLD}{bcolors.BRIGHT_BLUE}-- Basic testing --{bcolors.DEFAULT}')
    Test('Test sanity').assert_equal(1,1)

def test_register():
    print(f'{bcolors.BOLD}{bcolors.BRIGHT_BLUE}-- Register testing --{bcolors.DEFAULT}')

    Test('Read single register').assert_equal(sensor._who_am_i, 0xB3)
    Test('Read multiple register').assert_equal(sensor._rpds, 0x0000)

    sensor._rpds = 0xAB
    Test('Write single register').assert_equal(sensor._rpds, 0xAB)
    #clean up
    sensor._rpds = 0x00
    Test('Write single register').assert_equal(sensor._rpds, 0x00)

    sensor._rpds = 0xABCD
    Test('Write multiple register').assert_equal(sensor._rpds, 0xABCD)

    #clean up
    sensor._rpds = 0x0000
    Test('Clean up').assert_equal(sensor._rpds, 0x00)



def test_register_bits():
    print(f'{bcolors.BOLD}{bcolors.BRIGHT_BLUE}-- Register Bits testing --{bcolors.DEFAULT}')

    Test('Read single bit (low)').assert_equal(sensor._swreset, 0)
    Test('Read single bit (high)').assert_equal(sensor._if_add_inc, 1)

    
    sensor._bdu = 1
    Test('Write single bit (high)').assert_equal(sensor._bdu, 1)
    sensor._bdu = 0
    Test('Write single bit (low)').assert_equal(sensor._bdu, 0)

    sensor._odr = 3
    Test('Multiple bits').assert_equal(sensor._odr, 3)
    

def test_functionnality():
    print(f'{bcolors.BOLD}{bcolors.BRIGHT_BLUE}-- Functionnalities --{bcolors.DEFAULT}')
   
    # Device Id
    Test('Read single register').assert_equal(sensor.device_id, 0xB3)
 

    # FIFO
    sensor.fifo_watermark = 0xAB
    Test('Set FIFO watermark').assert_equal(sensor._fifo_wtm, 0xAB)
    Test('Read FIFO watermark').assert_equal(sensor.fifo_watermark, 0XAB)


    # Reset
    # The reset procedure clears multiple regiters,
    # but only the fifo wtm is tested
    sensor.fifo_watermark = 0XAB
    sensor.reset()
    Test('Reset - fifo wtm').assert_equal(sensor.fifo_watermark, 0X00)

    # New measurement
    Test('No new measurement').assert_equal(sensor.new_pressure_data, 0x00)
    sensor.trigger_measurement()
    sleep(1)
    Test('Has new measurement').assert_equal(sensor.new_pressure_data, 0x01)


if __name__ == "__main__":
    cs_pin = Pin(1, Pin.OUT)
    spi = SPI(0, baudrate=1000000, firstbit=SPI.MSB, sck=Pin(2), mosi=Pin(3), miso=Pin(0))

    sensor = LPS22HH(spi, cs_pin)

    print(f'{bcolors.BOLD}{bcolors.BRIGHT_MAGENTA}Testing starts...{bcolors.DEFAULT}')

    test_basic()
    test_register()
    test_register_bits()
    test_functionnality()

