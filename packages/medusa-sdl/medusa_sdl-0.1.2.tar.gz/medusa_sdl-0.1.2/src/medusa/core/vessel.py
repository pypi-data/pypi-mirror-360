__authors__ = "Anji Zhang (@atozhang), Felix Strieth-Kalthoff (@felix-s-k), Martin Seifrid (@mseifrid)"

from typing import Union
from ..utils import RangeError, HardwareError


class Vessel:
    """
    Defines a vessel, which may be a solution container, a reaction vial, a N2 tank, or a waste bottle.
    """

    def __init__(
            self,
            addable: bool,
            removable: bool,
            max_volume: Union[float, int],
            current_volume: Union[float, int] = 0.0,
            min_volume: Union[float, int] = 0.0,
            content: str = "empty"
    ):
        """
        Initializes a vessel object.

        Args:
            addable: Whether the vessel can be added to.
            removable: Whether the vessel can be drawn from.
            max_volume: The maximum volume of the vessel.
            current_volume: The current volume of the vessel.
            min_volume: The minimum volume of the vessel.
        """
        self._addable, self._removable = addable, removable
        self._min_volume, self._max_volume = min_volume, max_volume
        self._current_volume = current_volume
        self._content = content

    @property
    def volume(self) -> float:
        """
        Returns the current volume of the vessel.
        """
        return self._current_volume

    @property
    def total_volume(self) -> float:
        """
        Returns the total volume of the vessel.
        """
        return self._max_volume

    @property
    def min_volume(self) -> float:
        """
        Returns the minimum volume of the vessel.
        """
        return self._min_volume

    def validate_transfer(self, volume: float, direction: str):
        """
        Validates a liquid transfer.

        Args:
            volume: The volume to transfer.
            direction: The direction of the transfer ("add" or "remove").
        """
        if direction == "add":
            if not self._addable:
                raise HardwareError("This vessel is not addable.")
            if volume + self._current_volume > self._max_volume:
                raise RangeError(f"The resulting volume {volume + self._current_volume} from this transfer would exceed"
                                 f" the vessel's max volume of {self._max_volume}")

        elif direction == "remove":
            if not self._removable:
                raise HardwareError("This vessel is not removable.")
            if self._current_volume - volume < self._min_volume:
                raise RangeError(f"The resulting volume {self._current_volume - volume} from this transfer would be "
                                 f"below the vessel's minimum volume of {self._min_volume}")

        else:
            raise ValueError("Direction must be either 'add' or 'remove'.")

    def update_volume(self, volume: float, direction: str):
        """
        Updates the volume of the vessel.

        Args:
            volume: The volume to transfer.
            direction: The direction of the transfer ("add" or "remove").
        """
        if direction == "remove":
            volume = -volume

        self._current_volume += volume

    @property
    def content(self) -> str:
        """
        Returns the current content of the vessel
        """
        return self._content

    @content.setter
    def content(self, content: str):
        """
        Update the content of the vessel
        """
        self._content = content