from abc import ABC, abstractmethod


class HeatStirPlate(ABC):
    category="Hotplate"
    min_rpm: int

    _temp_query: str
    _temp_set: str
    _heat_start: str
    _heat_stop: str
    _rpm_query: str
    _rpm_set: str
    _stir_start: str
    _stir_stop: str

    _switch_temp: int = 0
    _switch_rpm: int = 0

    def __init__(self, max_temp: float, max_rpm: float) -> None:
        """
        Abstract base class for heat/stir plates.

        Args:
            max_temp: Maximum allowable temperature
            max_rpm: Maximum allowable stirring speed

        Returns:
            None
        """
        self._target_temp: int
        self._heat_switch_status: bool
        self._target_rpm: int
        self._stir_switch_status: bool

        self.max_temp: float = max_temp
        self.max_rpm: float = max_rpm

    @abstractmethod
    def _write_hotplate(self, command: str) -> None:
        pass

    @abstractmethod
    def _query_hotplate(self, command: str) -> str:
        pass

    def stand_by(self) -> None:
        """
        Sets the hotplate to stand-by mode by turning of heating and stirring.

        Returns:
            None
        """
        self.temp = self._switch_temp
        self.rpm = self._switch_rpm

    @property
    @abstractmethod
    def temp(self) -> float:
        pass

    @temp.setter
    @abstractmethod
    def temp(self, temp: float) -> None:
        pass

    @property
    @abstractmethod
    def target_temp(self) -> float:
        pass

    @property
    @abstractmethod
    def _heat_switch(self) -> bool:
        pass

    @_heat_switch.setter
    @abstractmethod
    def _heat_switch(self, heat_switch_status: bool) -> None:
        pass

    @property
    @abstractmethod
    def rpm(self) -> int:
        pass

    @rpm.setter
    @abstractmethod
    def rpm(self, rpm: int) -> None:
        pass

    @property
    @abstractmethod
    def target_rpm(self) -> int:
        pass

    @property
    @abstractmethod
    def _stir_switch(self) -> bool:
        pass

    @_stir_switch.setter
    @abstractmethod
    def _stir_switch(self, stir_switch_status: bool):
        pass
