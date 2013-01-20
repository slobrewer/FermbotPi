# -*- coding: utf-8 -*-
import os, logging, datetime, inspect, errno
import sqlite3 as lite
from decimal import Decimal

RPI_BUS_PATH = "/sys/devices/w1_bus_master1"

DS18B20_1_WIRE_TYPE = 0x28
DS18B20_1_WIRE_TYPE_PREFIX = hex(DS18B20_1_WIRE_TYPE).replace("0x", "", 1)

SLAVE_LIST_FILE_PATH = "/w1_master_slaves"
TEMPERATURE_FILE_PATH = "/w1_slave"

cwd = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
THERMO_LOGGER_SQL_FILE = os.path.join(cwd, "thermo_logger.sql") 


class Thermometer(object):
    def __init__(self, bus_master_path, serial):
        self._serial = ""
        self._bus_master_path = ""
        
        self.bus_master_path = bus_master_path
        self.serial = serial
       
    # Serial property
    @property
    def serial(self):
        """Return a string of the 1-wire serial number for the thermometer""" 
        return self._serial
    
    @serial.setter
    def serial(self, value):
        """Set the 1-wire serial number for the thermometer""" 
        if not isinstance(value, str):
            raise TypeError("Serial must be a string")
        if not value.startswith(DS18B20_1_WIRE_TYPE_PREFIX + "-"):
            raise ValueError("Only type " + DS18B20_1_WIRE_TYPE_PREFIX +
                             " 1-wire devices are supported.")
        self._serial = value
        return self._serial
    
    # Bus Master Path property
    @property
    def bus_master_path(self):
        """Return a string of the file system path to the 1-wire bus master"""
        return self._bus_master_path
    
    @bus_master_path.setter
    def bus_master_path(self, value):
        """Set the file system path to the 1-wire bus master"""
        if not os.access(value, os.F_OK):
            raise ValueError("bus_master_path '" + value +
                             "' doesn't point to a directory")
        
        if not value.endswith("/"):
            value += "/"
        
        self._bus_master_path = value
        return self._bus_master_path
    
    # Temperature in Celcius property
    @property
    def temp_c(self):
        """Returns a Decimal that is the current temperature in degrees Celcius
        
        
        Queries the 1-wire bus files.  Precision is to the 1000th of a
        degree but accuracy is only to +/-0.5 C.
        """
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
    
    # Temperature in Fahrenheit property
    @property
    def temp_f(self):
        """Return a Decimal that is the current temperature in degrees Farenheit
        
        Queries the 1-wire bus files.  Precision is to the 1000th of a degree
        but accuracy is only to +/-0.5 C.
        """
        return ((self.temp_c * Decimal(9) / Decimal(5)) +
                Decimal(32)).quantize(Decimal('1.000'))

class TempReadingError(Exception):
    def __init__(self, msg):
        self.msg = msg

class ThermoLogger(object):
    def __init__(self):
        self._next = None
        
    # Next logger property
    @property
    def next(self):
        return self._next
    
    @next.setter
    def next(self, value):
        self._next = value
        return self._next
    
    def add_logger(self, logger):
        if (self.next == None):
            self.next = logger
        else:
            self.next.add_logger(logger)
    
    def log_thermo(self, thermo):
        """Log the data from the Thermometer to all configured logs"""
        self._log_thermo_without_chain(thermo)
        
        if (self.next != None):
            self.next.log_thermo(thermo)
    
    def _log_thermo_without_chain(self, thermo):
        """Log the data from the Thermometer for the current class without
        calling down the logging chain.  Subclasses must implement this method
        """
        raise TypeError('Abstract method `' + self._class.__name__ \
                            + '.' + self._function + '\' called')

class FileThermoLogger(ThermoLogger):
    def __init__(self, app_name):
        """Create a Python logging based temperature logger with configured
        logged application name app_name"""
        super(FileThermoLogger, self).__init__()
        self._app_name = ""
        
        self.app_name = app_name
    
    # The application name configured in the logging configuration property
    @property
    def app_name(self):
        return self._app_name;
    
    @app_name.setter
    def app_name(self, value):
        self._app_name = value
        return self._app_name
    
    def _log_thermo_without_chain(self, thermo):
        """Log the thermometer serial, temp, and time to a log file"""
        logger = logging.getLogger(self.app_name)
        logger.info("%s at %.1f° F" % (thermo.serial, thermo.temp_f))

# SQLite3/decimal.Decimal converters        
def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return Decimal(s)

lite.register_adapter(Decimal, adapt_decimal)
lite.register_converter("decimal", convert_decimal)

class SQLThermoLogger(ThermoLogger):

    def __init__(self, db_file):
        """Create a SQLite3 based temperature logger using database file
        named dbFile"""
        super(SQLThermoLogger, self).__init__()

        self._db_file = ""
        
        self.db_file = db_file
        try:
            self.initDatabase()
        except:
            print 'Something has gone wrong initializing the database'
            raise
    
    # The path to the database file property
    @property
    def db_file(self):
        return self._db_file
    
    @db_file.setter
    def db_file(self, value):
        self._db_file = value
        return self._db_file
    
    def _log_thermo_without_chain(self, thermo):
        with lite.connect(self.db_file,
                          detect_types=lite.PARSE_DECLTYPES) as conn:
            conn.execute("""INSERT INTO temperature_points(thermometer_serial,
                         record_time, temp_celcius)
                         VALUES (?, ?, ?)""",
                         (thermo.serial, datetime.datetime.now(),
                          thermo.temp_c))
 
    def initDatabase(self):
        try:
            os.makedirs(os.path.dirname(self.db_file))
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(
                os.path.dirname(self.db_file)):
                pass
            else: raise

        self._conn = lite.connect(self.db_file)
        c = self._conn.cursor()
        with open(THERMO_LOGGER_SQL_FILE, 'r') as init_file:
            init_query = init_file.read()
        c.executescript(init_query)


def get_thermometers(bus_master_path):
    thermometers = []
    with open(bus_master_path + SLAVE_LIST_FILE_PATH) as w1_master_slaves_file:
        for slave in w1_master_slaves_file:
            if slave.startswith(DS18B20_1_WIRE_TYPE_PREFIX):
                thermometers.append(Thermometer(bus_master_path,
                                                slave.strip()))
                
    return thermometers