#!/usr/bin/python
# -*- coding: utf-8 -*-

# Running this script retrieves the temperatures for all attached thermometers
# and logs the results.  This is intended to be called by a cron job
# so only runs through once on each call

import thermo, logging.config
import fermbot_thermo_settings as settings
from datetime import datetime

LOG_CONFIG_FILE = "logging.conf"

# Debugging constants
if settings.DEBUG:
    DEVICE_PATH = "../tests/data/thermo/dual_thermo_bus_master"
else:
    DEVICE_PATH = thermo.RPI_BUS_PATH


def main():
    logging.config.fileConfig(LOG_CONFIG_FILE)
    
    for thermometer in thermo.get_thermometers(DEVICE_PATH):
        thermo_logger = thermo.FileThermoLogger()
        thermo_logger.log_thermo(thermometer)


if __name__ == '__main__':
    main()