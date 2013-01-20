# -*- coding: utf-8 -*-
import pytest, fermbot.thermo, decimal, logging.config, inspect, os
import sqlite3 as lite
from decimal import Decimal

cwd = os.path.dirname(os.path.abspath(inspect.getfile(
                   inspect.currentframe())))
SINGLE_THERMO_BUS_PATH = os.path.join(cwd,
                                      "data/thermo/single_thermo_bus_master")
DUAL_THERMO_BUS_PATH = os.path.join(cwd, "data/thermo/dual_thermo_bus_master")
BAD_CRC_THERMO_BUS_PATH = os.path.join(cwd,
                                       "data/thermo/bad_crc_thermo_bus_master")

FILE_LOGGER_LOG_FILE = os.path.join(cwd, "fermbot_thermo.log")
LOG_CONFIG_FILE = os.path.join(cwd, "../fermbot/logging.conf")
logging.config.fileConfig(LOG_CONFIG_FILE)
LOGGING_APP_NAME = "fermbotThermoTest"

SQL_LOGGER_FILE = os.path.join(cwd, "test.db")

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
    assert thermometers[0].temp_c == Decimal("19.562")
    
def test_thermometer_multiple_temp_c():
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    assert thermometers[0].temp_c == Decimal("19.562")
    assert thermometers[1].temp_c == Decimal("18.125")
        
def test_thermometer_temp_c_bad_crc():
    thermometers = fermbot.thermo.get_thermometers(BAD_CRC_THERMO_BUS_PATH)
    with pytest.raises(fermbot.thermo.TempReadingError): #@UndefinedVariable
        thermometers[0].temp_c
    
def test_thermometer_temp_f():
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)
    assert thermometers[0].temp_f == Decimal("67.212")
    
def test_thermometer_multiple_temp_f():
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    assert thermometers[0].temp_f == Decimal("67.212")
    assert thermometers[1].temp_f == Decimal("64.625")
        
def test_thermometer_temp_f_bad_crc():
    thermometers = fermbot.thermo.get_thermometers(BAD_CRC_THERMO_BUS_PATH)
    with pytest.raises(fermbot.thermo.TempReadingError): #@UndefinedVariable
        thermometers[0].temp_f

class ListThermoLogger(fermbot.thermo.ThermoLogger):
    """Simple ThermoLogger implementation that stores the temperatures in
    a list"""
    def __init__(self):
        super(ListThermoLogger, self).__init__()
        self._log_entries = []
    
    # Log Entries property
    @property
    def log_entries(self):
        """Return a list of the entries in the log"""
        return self._log_entries
    
    # Overrides for ThermoLogger
    def _log_thermo_without_chain(self, thermo):
        """Log the temperature from the thermometer"""
        self.log_entries.append(thermo.temp_f)

def test_logger_simple_log():
    thermo_logger = ListThermoLogger()
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    
    for thermometer in thermometers:
        thermo_logger.log_thermo(thermometer)
    
    assert len(thermo_logger.log_entries) == 2
    assert thermo_logger.log_entries[0] == Decimal("67.212")
    assert thermo_logger.log_entries[1] == Decimal("64.625")

def test_logger_file_log():
    thermo_logger = fermbot.thermo.FileThermoLogger(LOGGING_APP_NAME)
    thermometers = fermbot.thermo.get_thermometers(SINGLE_THERMO_BUS_PATH)

    thermo_logger.log_thermo(thermometers[0])
    
    with open(FILE_LOGGER_LOG_FILE) as log_file:
        last_line = ""
        for line in log_file:
            last_line = line
        
        assert (" ".join(last_line.split()[-4:]) ==
                "28-0000041481e8 at 67.2° F")

def test_logger_sql_log():
    thermo_logger = fermbot.thermo.SQLThermoLogger(SQL_LOGGER_FILE)
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)

    for thermometer in thermometers:
        thermo_logger.log_thermo(thermometer)
    
    with lite.connect(SQL_LOGGER_FILE,
                      detect_types=lite.PARSE_DECLTYPES) as conn:
        conn.row_factory = lite.Row
        cur = conn.cursor()
        cur.execute("""SELECT * FROM temperature_points
                    ORDER BY record_time DESC""")
        r = cur.fetchone()
        assert r['temp_celcius'] == Decimal("18.125")
        assert r['thermometer_serial'] == "28-0000041462fa"
        r = cur.fetchone()
        assert r['temp_celcius'] == Decimal("19.562")
        assert r['thermometer_serial'] == "28-0000041481e8"
 
def test_logger_chained_log():
    thermo_logger_1 = ListThermoLogger()
    thermo_logger_2 = ListThermoLogger()
    thermo_logger_3 = ListThermoLogger()
    thermo_logger_1.add_logger(thermo_logger_2)
    thermo_logger_1.add_logger(thermo_logger_3)
    thermometers = fermbot.thermo.get_thermometers(DUAL_THERMO_BUS_PATH)
    
    for thermometer in thermometers:
        thermo_logger_1.log_thermo(thermometer)
    
    assert len(thermo_logger_1.log_entries) == 2
    assert thermo_logger_1.log_entries[0] == Decimal("67.212")
    assert thermo_logger_1.log_entries[1] == Decimal("64.625")
    assert len(thermo_logger_2.log_entries) == 2
    assert thermo_logger_2.log_entries[0] == Decimal("67.212")
    assert thermo_logger_2.log_entries[1] == Decimal("64.625")
    assert len(thermo_logger_3.log_entries) == 2
    assert thermo_logger_3.log_entries[0] == Decimal("67.212")
    assert thermo_logger_3.log_entries[1] == Decimal("64.625")
