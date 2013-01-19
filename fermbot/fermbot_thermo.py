#!/usr/bin/python
# -*- coding: utf-8 -*-

# Running this script retrieves the temperatures for all attached thermometers
# and logs the results.  This is intended to be called by a cron job
# so only runs through once on each call

import thermo, logging.config, inspect, os
import fermbot_thermo_settings as settings

cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
LOG_CONFIG_FILE = os.path.join(cwd, "logging.conf")

# Debugging constants
if settings.DEBUG:
    DEVICE_PATH = os.path.join(cwd,
                               "../tests/data/thermo/dual_thermo_bus_master")
    LOGGING_APP_NAME = "fermbotThermoDebug"
else:
    DEVICE_PATH = thermo.RPI_BUS_PATH
    LOGGING_APP_NAME = "fermbotThermoApp"


def main():
    logging.config.fileConfig(LOG_CONFIG_FILE)
    
    for thermometer in thermo.get_thermometers(DEVICE_PATH):
        thermo_logger = thermo.FileThermoLogger()
        thermo_logger.log_thermo(thermometer, LOGGING_APP_NAME)


if __name__ == '__main__':
    main()