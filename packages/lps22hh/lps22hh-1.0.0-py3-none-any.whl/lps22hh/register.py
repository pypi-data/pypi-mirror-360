# Author: Chris Braissant
#
# Register library for:
# Driver for the ST LPS22HH:
# High-performance MEMS nano pressure sensor:
# 260-1260 hPa absolute digital output barometer

class Bits:
    def __init__(self, register_address, start_position:int, length:int):
        self.register_address = register_address
        self.start_position = start_position
        self.length = length
        self.mask = ((1 << self.length) - 1) << self.start_position

    def __get__(self, obj, objtype=None):
        reg = Register(self.register_address, 1)
        data = reg.__get__(obj)
        data &= self.mask
        data >>= self.start_position
        return data 

    def __set__(self, obj, value):
        reg = Register(self.register_address, 1)
        data = reg.__get__(obj)
        # clear the bits to write
        data &= ~self.mask 
        # write the new value
        data |= (value << self.start_position)
        reg.__set__(obj, data)



class Register:
    def __init__(self, register_address:int, length:int):
        self.register_address = register_address
        self.length = length
                
    def __get__(self, obj, objtype=None):
        if hasattr(obj, 'spi'):
            addr = 0x80 | self.register_address
            msg = addr.to_bytes(1, 'little')
            obj.cs.off()
            obj.spi.write(msg)
            data = obj.spi.read(self.length)
            obj.cs.on()
            return int.from_bytes(data, 'little')
        elif hasattr(obj, 'i2c'):
            data = obj.i2c.readfrom_mem(obj.i2c_addr, self.register_address, self.length)
            return int.from_bytes(data, 'little')
        else:
            raise AttributeError("Interface not defined")


    def __set__(self, obj, data):
        data_bytes = data.to_bytes(self.length, 'little')
        if hasattr(obj, 'spi'):
            msg = bytearray()
            msg.append(self.register_address)
            msg.extend(data_bytes)
            obj.cs.off()
            obj.spi.write(msg)
            obj.cs.on()
        elif hasattr(obj, 'i2c'):
            obj.i2c.writeto_mem(obj.i2c_addr, self.register_address, data_bytes)
        else:
            raise AttributeError("Interface not defined")