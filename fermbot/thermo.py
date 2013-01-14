'''
Created on Jan 13, 2013

@author: dlouw
'''

RPI_BUS_PATH = "/sys/devices/w1_bus_master1"

DS18B20_1_WIRE_TYPE = 0x28
DS18B20_1_WIRE_TYPE_PREFIX = hex(DS18B20_1_WIRE_TYPE).replace("0x", "", 1)

SLAVE_LIST_FILE_PATH = "/w1_master_slaves"

class Thermometer:
    def __init__(self, serial):
        self.serial = serial
        
    serial = ""
    
def get_thermometers(bus_master_path):
    thermometers = []
    with open(bus_master_path + SLAVE_LIST_FILE_PATH) as w1_master_slaves_file:
        for slave in w1_master_slaves_file:
            if slave.startswith(DS18B20_1_WIRE_TYPE_PREFIX):
                thermometers.append(Thermometer(slave.strip()))
                
    return thermometers