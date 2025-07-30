import pytest
from matterlab_hotplates.base_hotplate import HeatStirPlate


class MockHotplate(HeatStirPlate):
    def _write_hotplate(self, command: str) -> None:
        pass

    def _query_hotplate(self, command: str) -> str:
        return ""

    @property
    def temp(self) -> float:
        return 20.0

    @temp.setter
    def temp(self, temp: float) -> None:
        pass

    @property
    def target_temp(self) -> float:
        return 42.0

    @property
    def _heat_switch(self) -> bool:
        return False

    @_heat_switch.setter
    def _heat_switch(self, heat_switch_status: bool) -> None:
        pass

    @property
    def rpm(self) -> int:
        return 0

    @rpm.setter
    def rpm(self, rpm: int) -> None:
        pass

    @property
    def target_rpm(self) -> int:
        return 1000

    @property
    def _stir_switch(self) -> bool:
        return False

    @_stir_switch.setter
    def _stir_switch(self, stir_switch_status: bool):
        pass


def test_heat_stir_plate_abstract_methods():
    with pytest.raises(TypeError):
        HeatStirPlate(max_temp=100, max_rpm=1000)


def test_heat_stir_plate_instantiation():
    hotplate = MockHotplate(max_temp=100, max_rpm=1000)
    assert isinstance(hotplate, HeatStirPlate)
    assert hotplate.max_temp == 100
    assert hotplate.max_rpm == 1000
    assert hotplate._switch_temp == 0
    assert hotplate._switch_rpm == 0


def test_heat_stir_plate_read():
    hotplate = MockHotplate(max_temp=100, max_rpm=1000)
    assert hotplate.temp == 20.0
    assert hotplate.rpm == 0


def test_heat_stir_plate_targets():
    hotplate = MockHotplate(max_temp=100, max_rpm=1000)
    assert hotplate.target_temp == 42.0
    assert hotplate.target_rpm == 1000
