import time
from abc import ABC, abstractmethod
from typing import Union, Optional, Dict


class Relay(ABC):
    """
    Abstract Base Class for handling different kinds of syringe pumps.
    """
    category="Relay"
    def __init__(self):
        pass

    @abstractmethod
    def on(self) -> bool:
        """
        abstract method to get the normal_open or closed status of a relay channel
        :return:
        """
        pass

