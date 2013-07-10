#!/usr/bin/python
# -*- coding: utf-8 -*-

# Running this script retrieves the temperatures for all attached thermometers
# and logs the results.  Additionally this script applies the appropriate
# temperature control logic to turn on or off controllers.  This is intended to
# be called by a cron job so only runs through once on each call

import thermo, logging.config, inspect, os
import fermbot_thermo_settings as settings

cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
LOG_CONFIG_FILE = os.path.join(cwd, "logging.conf")

# Debugging constants
if settings.DEBUG:
    DEVICE_PATH = os.path.join(cwd,
                               "../tests/data/thermo/dual_thermo_bus_master")
    LOGGING_APP_NAME = "fermbotThermoDebug"
    SQL_LOGGER_DB_FILE = os.path.join(cwd, "test.db")
else:
    DEVICE_PATH = thermo.RPI_BUS_PATH
    LOGGING_APP_NAME = "fermbotThermoApp"
    SQL_LOGGER_DB_FILE = "/var/lib/fermbot/fermbot_thermo.db"

def main():
    logging.config.fileConfig(LOG_CONFIG_FILE)
    
    thermo_logger = thermo.FileThermoLogger(LOGGING_APP_NAME)
    thermo_logger.add_logger(thermo.SQLThermoLogger(SQL_LOGGER_DB_FILE))
    
    for thermometer in thermo.get_thermometers(DEVICE_PATH):
        thermo_logger.log_thermo(thermometer)

    # TODO: Currently set to the last controller, set more intelligently
    temp_controller = thermo.TempControllerFactory.simpleCoolingController(
        DEVICE_PATH, settings.MAX_TEMP_F)
    temp_controller.process()
    thermo_logger.log_temp_controller(temp_controller)

if __name__ == '__main__':
    main()