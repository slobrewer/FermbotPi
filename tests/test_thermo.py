# -*- coding: utf-8 -*-
import pytest, fermbot.thermo, decimal, logging.config

SINGLE_THERMO_BUS_PATH = "data/thermo/single_thermo_bus_master"
DUAL_THERMO_BUS_PATH = "data/thermo/dual_thermo_bus_master"
BAD_CRC_THERMO_BUS_PATH = "data/thermo/bad_crc_thermo_bus_master"

FILE_LOGGER_LOG_FILE = "fermbot_thermo.log"
logging.config.fileConfig('../fermbot/logging.conf')

def test_get_thermometers_exactly_one():
    assert len(fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)) == 1

def test_get_thermometers_exactly_two():
    assert len(fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)) == 2
    
def test_get_thermometers_check_name_single():
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)
    assert len(fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)) == 1
    assert thermometers[0].serial == "28-0000041481e8"
        
def test_get_thermometers_check_names_double():
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    assert len(fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)) == 2
    assert thermometers[0].serial == "28-0000041481e8"
    assert thermometers[1].serial == "28-0000041462fa"
    
def test_thermometer_temp_c():
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)
    assert thermometers[0].temp_c == decimal.Decimal("19.562")
    
def test_thermometer_multiple_temp_c():
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    assert thermometers[0].temp_c == decimal.Decimal("19.562")
    assert thermometers[1].temp_c == decimal.Decimal("18.125")
        
def test_thermometer_temp_c_bad_crc():
    thermometers = fermbot.thermo.get_thermometers(BAD_CRC_THERMO_BUS_PATH)
    with pytest.raises(fermbot.thermo.TempReadingError): #@UndefinedVariable
        thermometers[0].temp_c
    
def test_thermometer_temp_f():
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)
    assert thermometers[0].temp_f == decimal.Decimal("67.212")
    
def test_thermometer_multiple_temp_f():
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    assert thermometers[0].temp_f == decimal.Decimal("67.212")
    assert thermometers[1].temp_f == decimal.Decimal("64.625")
        
def test_thermometer_temp_f_bad_crc():
    thermometers = fermbot.thermo.get_thermometers(BAD_CRC_THERMO_BUS_PATH)
    with pytest.raises(fermbot.thermo.TempReadingError): #@UndefinedVariable
        thermometers[0].temp_f

class ListThermoLogger(fermbot.thermo.ThermoLogger):
    """Simple ThermoLogger implementation that stores the temperatures in
    a list"""
    def __init__(self):
        pass
    
    # Log Entries property
    _log_entries = []
    
    @property
    def log_entries(self):
        """Return a list of the entries in the log"""
        return self._log_entries
    
    # Overrides for ThermoLogger
    def log_thermo(self, thermo):
        """Log the temperature from the thermometer"""
        self.log_entries.append(thermo.temp_f)

def test_logger_simple_log():
    thermo_logger = ListThermoLogger()
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)
    
    thermo_logger.log_thermo(thermometers[0])
    thermo_logger.log_thermo(thermometers[0])
    assert len(thermo_logger.log_entries) == 2
    assert thermo_logger.log_entries[0] == decimal.Decimal("67.212")
    assert thermo_logger.log_entries[1] == decimal.Decimal("67.212")

def test_logger_file_log():
    thermo_logger = fermbot.thermo.FileThermoLogger()
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)

    thermo_logger.log_thermo(thermometers[0])
    
    with open(FILE_LOGGER_LOG_FILE) as log_file:
        last_line = ""
        for line in log_file:
            last_line = line
        
        assert (" ".join(last_line.split()[-5:]) ==
                "Thermometer 28-0000041481e8 at 67.2° F")
        