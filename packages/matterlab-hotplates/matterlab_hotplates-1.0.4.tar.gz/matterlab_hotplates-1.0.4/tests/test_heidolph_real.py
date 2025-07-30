import pytest
from matterlab_hotplates.base_hotplate import HeatStirPlate
from matterlab_hotplates import HeidolphHotplate
import time


COM_PORT = "COM3"

def test_heat_stir_plate_instantiation():
    hotplate = HeidolphHotplate(com_port=COM_PORT, max_temp=100, max_rpm=1000)
    assert isinstance(hotplate, HeatStirPlate)
    assert hotplate.max_temp == 100
    assert hotplate.max_rpm == 1000
    assert hotplate._switch_temp == 0
    assert hotplate._switch_rpm == 0


def test_heat_stir_plate_read():
    hotplate = HeidolphHotplate(com_port=COM_PORT, max_temp=100, max_rpm=1000)
    assert hotplate.target_temp == 0
    assert hotplate.rpm == 0


def test_heat_stir_plate_targets():
    hotplate = HeidolphHotplate(com_port=COM_PORT, max_temp=100, max_rpm=1000)
    # assert hotplate.target_temp == 42.0
    # assert hotplate.target_rpm == 1000
    hotplate.rpm = 200
    time.sleep(5)
    assert hotplate.rpm == 200
    hotplate.rpm = 0
    hotplate.stand_by()
    time.sleep(3)
    assert hotplate.rpm == 0
