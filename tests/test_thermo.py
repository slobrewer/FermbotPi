import pytest
import fermbot.thermo

SINGLE_THERMO_BUS_PATH = "data/thermo/single_thermo_bus_master"
DUAL_THERMO_BUS_PATH = "data/thermo/dual_thermo_bus_master"

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