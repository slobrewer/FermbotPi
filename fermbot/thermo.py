import os

from decimal import Decimal

RPI_BUS_PATH = "/sys/devices/w1_bus_master1"

DS18B20_1_WIRE_TYPE = 0x28
DS18B20_1_WIRE_TYPE_PREFIX = hex(DS18B20_1_WIRE_TYPE).replace("0x", "", 1)

SLAVE_LIST_FILE_PATH = "/w1_master_slaves"
TEMPERATURE_FILE_PATH = "/w1_slave"

class Thermometer(object):
    def __init__(self, bus_master_path, serial):
        self.bus_master_path = bus_master_path
        self.serial = serial
    
    # Serial property: the unique 1-wire serial number for the thermometer    
    _serial = ""
    
    @property
    def serial(self):
        return self._serial
    
    @serial.setter
    def serial(self, value):
        if not isinstance(value, str):
            raise TypeError("Serial must be a string")
        if not value.startswith(DS18B20_1_WIRE_TYPE_PREFIX + "-"):
            raise ValueError("Only type " + DS18B20_1_WIRE_TYPE_PREFIX +
                             " 1-wire devices are supported.")
        self._serial = value
    
    # Bus Master Path property: the file system path to the 1-wire bus master
    _bus_master_path = ""
    
    @property
    def bus_master_path(self):
        return self._bus_master_path
    
    @bus_master_path.setter
    def bus_master_path(self, value):
        if not os.access(value, os.F_OK):
            raise ValueError("bus_master_path '" + value +
                             "' doesn't point to a directory")
        
        if not value.endswith("/"):
            value += "/"
        
        self._bus_master_path = value
        pass
    
    # Temperature in Celcius property: provides the current temperature in
    # degrees Celcius by querying the 1-wire bus files.  Precision is to the
    # 1000th of a degree but accuracy is only to +/-0.5 C.
    @property
    def temp_c(self):
        with open(self.bus_master_path + self.serial +
                  TEMPERATURE_FILE_PATH) as temperature_file:
            crc_line = temperature_file.readline();
            temp_line = temperature_file.readline();
            temperature_file.close()

            crc = crc_line.split()[-1]

            if crc.split()[-0] == "NO":
                raise TempReadingError("Bad reading from thermometer '" +
                                       self.serial + "'")
            
            temperature_data = temp_line.split()[-1]
            return (Decimal(temperature_data[2:]) /
                Decimal(1000))
    
    # Temperature in Fahrenheit property: provides the current temperature in
    # degrees Farenheit by querying the 1-wire bus files.  Precision is to the
    # 1000th of a degree but accuracy is only to +/-0.5 C.
    @property
    def temp_f(self):
        return ((self.temp_c * Decimal(9) / Decimal(5)) +
                Decimal(32)).quantize(Decimal('1.000'))

class TempReadingError(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_thermometers(bus_master_path):
    thermometers = []
    with open(bus_master_path + SLAVE_LIST_FILE_PATH) as w1_master_slaves_file:
        for slave in w1_master_slaves_file:
            if slave.startswith(DS18B20_1_WIRE_TYPE_PREFIX):
                thermometers.append(Thermometer(bus_master_path,
                                                slave.strip()))
                
    return thermometers