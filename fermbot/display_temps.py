# -*- coding: utf-8 -*-
import time, glob, thermo
import display_temps_settings as settings
from datetime import datetime

# constants
if settings.DEBUG:
    DEVICE_PATH = "../tests/data/thermo/dual_thermo_bus_master"
else:
    DEVICE_PATH = thermo.RPI_BUS_PATH

def main():
    while True:
        for thermometer in thermo.get_thermometers(DEVICE_PATH):
            temperature_message = ""
            
            try:
                temperature_message =  "%.1f° F" % (thermometer.temp_f)
            except thermo.TempReadingError:
                temperature_message = "Failed to read temperature"
                
            print("[%s] %s: %s" %
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   thermometer.serial, temperature_message))
            
        time.sleep(settings.WAIT_SECS)

if __name__ == '__main__':
    main()
