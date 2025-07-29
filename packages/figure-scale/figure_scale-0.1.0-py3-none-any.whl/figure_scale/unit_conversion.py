"""Hold the table of conversion factors from other units to inches."""

from __future__ import annotations

from collections import UserDict
from fractions import Fraction
from typing import TYPE_CHECKING

from figure_scale.utils.singleton import singleton

if TYPE_CHECKING:
    from decimal import Decimal

    # Workaround needed for Python < 3.9 so it can be dropped in the future
    TypedUserDict = UserDict[str, Fraction]
else:
    TypedUserDict = UserDict

INITIAL_VALUES: dict[str, Fraction] = {
    "in": Fraction(1),
    "ft": Fraction(12),
    "yd": Fraction(36),
    "m": Fraction(10000, 254),
    "cm": Fraction(100, 254),
    "mm": Fraction(10, 254),
    "pt": Fraction(1, 72),
}


@singleton
class UnitConversionMapping(TypedUserDict):
    """
    A singleton dictionary class to hold the conversion factors from other units to inches.

    Examples:
        See the :ref:`User Guide<Unit Conversion>` for examples of how to use this class.
    """

    def __init__(self):
        super().__init__(**INITIAL_VALUES)

    def __setitem__(self, key: str, item: float | str | Decimal | Fraction) -> None:
        if not isinstance(key, str):
            raise TypeError("All keys must be strings.")
        try:
            fraction = Fraction(item)
        except (ValueError, TypeError) as e:
            raise ValueError(
                "The provided value can not be converted to a fraction."
            ) from e
        if fraction <= 0:
            raise ValueError("All values must be positive non-zero numbers.")
        return super().__setitem__(key, fraction)

    def __getitem__(self, key: str) -> Fraction:
        try:
            return super().__getitem__(key)
        except KeyError:
            raise KeyError(
                f"Unknown unit on {self.__class__.__name__}: {key}. The available options are: {', '.join(self)}"
            )
