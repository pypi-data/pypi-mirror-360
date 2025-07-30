import time
from typing import Union

from matterlab_serial_device import SerialDevice, open_close
from matterlab_hotplates.base_hotplate import HeatStirPlate


class IKAHotplate(HeatStirPlate, SerialDevice):
    category="Hotplate"
    ui_fields  = ("com_port", "address")
    min_rpm: int = 0  # Minimum RPM of IKA hotplate
    _temp_query: str = "IN_PV_1"
    _temp_set: str = "OUT_SP_1"
    _heat_start: str = "START_1"
    _heat_stop: str = "STOP_1"
    _rpm_query: str = "IN_PV_4"
    _rpm_set: str = "OUT_SP_4"
    _stir_start: str = "START_4"
    _stir_stop: str = "STOP_4"

    def __init__(
        self,
        com_port: str,
        max_temp: int = 200,
        max_rpm: int = 1700,
        connect_hardware: bool = True,
        encoding: str = "utf-8",
        baudrate: int = 9600,
        timeout: float = 1.0,
        parity: str = "even",
        bytesize: int = 7,
        stopbits: int = 1,
        **kwargs,
    ) -> None:
        """
        Controller for IKA hotplates.

        Args:
            com_port: COM port to be passed to SerialDevice
            max_temp: maximum temperature of the hotplate
            max_rpm: maximum RPM of the hotplate
            connect_hardware: whether to connect to the hardware on initialization
            encoding: encoding to be passed to SerialDevice
            baudrate: baudrate to be passed to SerialDevice
            timeout: timeout to be passed to SerialDevice
            parity: parity to be passed to SerialDevice
            bytesize: bytesize to be passed to SerialDevice
            stopbits: stopbits to be passed to SerialDevice
            **kwargs: additional keyword arguments to be passed to SerialDevice

        Returns:
            None
        """
        SerialDevice.__init__(
            self,
            com_port=com_port,
            encoding=encoding,
            baudrate=baudrate,
            timeout=timeout,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            **kwargs,
        )
        HeatStirPlate.__init__(self, max_temp=max_temp, max_rpm=max_rpm)

        if connect_hardware:
            self.stand_by()

    @open_close
    def _write_hotplate(self, command: str) -> None:
        """
        Method to write to the hotplate.

        Args:
            command: Command to write to the hotplate

        Returns:
            None
        """
        self.write(f"{command}\r\n")
        time.sleep(1)

    @open_close
    def _query_hotplate(self, command: str) -> str:
        """
        Method to query the hotplate.

        Args:
            command: Command to query the hotplate

        Returns:
            str: Response from the hotplate
        """
        return self.query(write_command=f"{command}\r\n", read_delay=0.5).split()[0]

    @property
    def temp(self) -> float:
        """
        Gets the temperature of the hotplate

        Returns:
            float: temperature of the hotplate
        """
        temp_reading: float = float(self._query_hotplate(self._temp_query))
        self.logger.info(f"Temperature reading on probe is {temp_reading}.")
        return temp_reading

    @temp.setter
    def temp(self, temp: Union[float, int]) -> None:
        """
        Sets the temperature of the hotplate

        Args:
            temp: nominal temperature of the hotplate

        Returns:
            None

        Raises:
            TypeError: if temperature is not a float or int
            ValueError: if temperature is out of range
        """
        if not isinstance(temp, (float, int)):
            raise TypeError("Temperature must be float or int!")

        if not self._switch_temp <= temp <= self.max_temp:
            raise ValueError(f"Temperature out of range: min {self._switch_temp}, max {self.max_temp}!")

        self._target_temp = temp
        self._write_hotplate(f"{self._temp_set} {temp:.1f}")
        self.logger.info(f"Target temperature set to {temp:.1f}.")

        if temp == self._switch_temp:
            self._heat_switch = False
        else:
            self._heat_switch = True

    @property
    def target_temp(self) -> float:
        """
        Returns:
            float: the target temperature of the hotplate
        """
        return self._target_temp

    @property
    def _heat_switch(self) -> bool:
        """
        Gets the heat switch status of the hotplate

        Returns:
            bool: heat switch status of the hotplate
        """
        self.logger.info(f"Heat switch is {self._heat_switch_status}.")
        return self._heat_switch_status

    @_heat_switch.setter
    def _heat_switch(self, heat_switch_status: bool):
        """
        Sets the heat switch status of the hotplate

        Args:
            heat_switch: heat switch status of the hotplate

        Returns:
            None
        """
        self._heat_switch_status = heat_switch_status
        if self._heat_switch_status:
            self._write_hotplate(self._heat_start)
            self.logger.info("Start heating.")
        else:
            self._write_hotplate(self._heat_stop)
            self.logger.info("Stop heating.")

    @property
    def rpm(self) -> int:
        """
        Gets the stir rate of the hotplate

        Returns:
            int: stir rate of the hotplate
        """
        rpm_read = int(float(self._query_hotplate(self._rpm_query)))
        self.logger.info(f"RPM reading is {rpm_read}.")
        return rpm_read

    @rpm.setter
    def rpm(self, rpm: int):
        """
        Sets the stir rate of the hotplate

        Args:
            rpm: nominal stir rate of the hotplate
        """
        if not isinstance(rpm, int):
            raise TypeError("rpm must be an integer")

        if not self._switch_rpm <= rpm <= self.max_rpm:
            raise ValueError(f"RPM out of range: min {self._switch_rpm}, max {self.max_rpm}!")

        self._target_rpm = rpm
        self._write_hotplate(f"{self._rpm_set} {rpm}")
        self.logger.info(f"Target rpm set to {rpm}.")

        if rpm == self._switch_rpm:
            self._stir_switch = False
        else:
            self._stir_switch = True

    @property
    def target_rpm(self):
        """
        Target stir rate of hotplate

        Returns:
            int: target stir rate of the hotplate
        """
        return self._target_rpm

    @property
    def _stir_switch(self) -> bool:
        """
        current stir switch of the hotplate
        :return:
        """
        self.logger.info(f"Stir switch is {self._stir_switch_status}.")
        return self._stir_switch_status

    @_stir_switch.setter
    def _stir_switch(self, stir_switch_status: bool):
        self._stir_switch_status = stir_switch_status
        if self._stir_switch_status:
            self._write_hotplate(self._stir_start)
            self.logger.info("Start stirring.")
        else:
            self._write_hotplate(self._stir_stop)
            self.logger.info("Stop stirring.")
