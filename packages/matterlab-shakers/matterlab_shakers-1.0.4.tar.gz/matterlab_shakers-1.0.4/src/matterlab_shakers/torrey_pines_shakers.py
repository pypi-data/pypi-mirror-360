import time
from typing import Union, Dict, List
from matterlab_serial_device import SerialDevice, open_close
from matterlab_shakers.base_shaker import Shaker


class TorreyPinesShaker(Shaker, SerialDevice):
    category="Shaker"
    ui_fields  = ("com_port")
    def __init__(
            self,
            com_port: str,
            max_temp: int = 110,
            min_temp: int = -20,
            connect_hardware: bool = True,
            encoding: str = "utf-8",
            baudrate: int = 9600,
            timeout: float = 1.0,
            parity: str = "none",
            bytesize: int = 8,
            stopbits: int = 1,
            errors: Dict = {
                "":     "Communication Error, receive empty feedback",
                "RTDo": "The RTD Sensor is not connected or has failed",
                "RTDs": "The RTD Sensor has shorted or has failed",
                "cal0": "The Calibrated Temperature Value is out of range",
                "cal1": "Low Cal Point out of range",
                "cal2": "High Cal Point out of range",
                "cal3": "High Point Measured Cal Value is Lower than Low Point Measured Value (or reverse)",
                "cal4": "High Point Temperature Value is Lower than Low Point Temperature Value (or reverse",
            },
            **kwargs
    ):
        """
        Controller for Torrey Pines Shaker
        :param com_port: COM port to be passed to SerialDevice
        :param max_temp: max temp of the shaker
        :param min_temp: min temp of the shaker
        :param connect_hardware: whether to connect to the hardware on initialization
        :param encoding: encoding to be passed to SerialDevice
        :param baudrate: baudrate to be passed to SerialDevice
        :param timeout: timeout to be passed to SerialDevice
        :param parity: parity to be passed to SerialDevice
        :param bytesize: bytesize to be passed to SerialDevice
        :param stopbits: stopbits to be passed to SerialDevice
        :param kwargs:
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
        Shaker.__init__(self, max_temp=max_temp, min_temp=min_temp, errors=errors)

        if connect_hardware:
            self.connect()

    def connect(self):
        model = self.device_model
        serial_number = self.device_serial_number
        if len(model) == 0 or len(serial_number) == 0:
            raise ConnectionError("Query shaker failed, check connection.")

    @open_close
    def _query_shaker(self, command: str) -> str:
        """
        Method to query the shaker
        :param command: command to query the shaker
        :return: response from the shaker
        """
        return self.query(write_command=f"{command}\r\n", remove_from_end=2, read_delay=0.5)

    @property
    def device_model(self) -> str:
        """
        Method to get device model
        :return: device model
        """
        device_model = self._query_shaker(command="v")
        self.logger.info(f"Device model is {device_model}")
        return device_model

    @property
    def serial_number(self) -> str:
        """
        Method to get serial number
        :return: serial numbe in str
        """
        serial_number = self._query_shaker(command="V")
        self.logger.info(f"Device serial number is {serial_number}")
        return serial_number

    @property
    def target_temp(self) -> float:
        """
        Gets the temperature target
        :return: temperature target
        """
        target_temp = self._query_shaker(command="s")
        if self.idle:
            return None
        else:
            self.logger.info(f"Temperature target is {target_temp}")
            return float(target_temp)

    @property
    def temp(self) -> float:
        """
        Get the current temperature of the plate
        :return: current temperature of the plate
        """
        temp = self._query_shaker(command="p")
        if temp in self.errors:
            self.error_reporting(temp)
        self.logger.info(f"Current plate temp is {temp}")
        return float(temp)

    @temp.setter
    def temp(self, temp: int):
        """
        Set the target temperature of the plate
        :param temp: target temp of the plate
        :return:
        """
        if (temp < self.min_temp) or (temp > self.max_temp):
            raise ValueError("Temp setting out of range")
        self.idle = False
        rtn = self._query_shaker(f"n{temp}")
        if rtn != "ok":
            time.sleep(1)
            if self.target_temp != temp:
                raise ValueError("Set temperature failed")
        self.logger.info(f"Temperature target set to {temp}")

    @property
    def idle(self) -> bool:
        """
        Get if the shaker is idle
        :return: shaker is idle True/False
        """
        idle = self._query_shaker("s")
        if idle == "off":
            self.logger.info("Shaker is idle")
            return True
        else:
            self.logger.info("Shaker is not idle")
            return False

    @idle.setter
    def idle(self, idle: bool):
        """
        Set/unset the shaker to idle
        :param idle: set to idle True/False
        :return:
        """
        if idle:
            rtn = self._query_shaker(command="i")
        else:
            rtn = self._query_shaker(command="I")
        if rtn != "ok":
            raise ValueError("Set idle status failed")

    @property
    def speed(self) ->int:
        """
        Get the orbital speed of the shaker
        :return: level of orbital speed, int 0-9, 0 is not moving, 9 is highest
        """
        speed = self._query_shaker(command="m")
        if speed in self.errors:
            self.error_reporting(speed)
        self.logger.info(f"Orbital speed is level {speed}")
        return int(speed)

    @speed.setter
    def speed(self, speed: int):
        """
        Set the orbital speed of the shaker
        :param speed: speed to set, int 0-9, 0 is not moving, 9 is highest
        :return:
        """
        if speed < 0 or speed > 9:
            raise ValueError("Orbital speed setting must be 0-9 level")
        rtn = self._query_shaker(command=f"m{speed}")
        if rtn in self.errors:
            self.error_reporting(rtn)
        self.logger.info(f"Orbital speed ste to level {speed}")

    def error_reporting(self, error: str):
        """
        report the errors
        :param error: error code get from the device
        :return:
        """
        raise ValueError(self.errors[error])

