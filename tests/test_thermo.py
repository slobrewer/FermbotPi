import pytest
import fermbot.thermo
import decimal

SINGLE_THERMO_BUS_PATH = "data/thermo/single_thermo_bus_master"
DUAL_THERMO_BUS_PATH = "data/thermo/dual_thermo_bus_master"
BAD_CRC_THERMO_BUS_PATH = "data/thermo/bad_crc_thermo_bus_master"

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
