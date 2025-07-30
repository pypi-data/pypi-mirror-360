from abc import ABC, abstractmethod


class Shaker(ABC):
    def __init__(self, max_temp: float, min_temp: float) -> None:
        """
        Abstract base class for shaker
        :param max_temp: max allowable temperature
        :param min_temp: min allowable temperature
        """
        self.max_temp = max_temp
        self.min_temp = min_temp

    @abstractmethod
    def _query_shaker(self, command: str) -> str:
        pass

    @property
    @abstractmethod
    def temp(self) -> float:
        pass

    @temp.setter
    @abstractmethod
    def temp(self, temp: float):
        pass

    @property
    @abstractmethod
    def target_temp(self) -> float:
        pass

    @property
    @abstractmethod
    def speed(self) -> int:
        pass

    @speed.setter
    @abstractmethod
    def speed(self, speed: int):
        pass

    @property
    @abstractmethod
    def idle(self) -> bool:
        pass

    @idle.setter
    @abstractmethod
    def idle(self, idle:bool):
        pass