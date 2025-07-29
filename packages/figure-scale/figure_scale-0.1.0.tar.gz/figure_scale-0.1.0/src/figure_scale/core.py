"""Module containing the core functionality of the project."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import NamedTuple, cast

from matplotlib.pyplot import rc_context, rcParams

from figure_scale.unit_conversion import UnitConversionMapping


class FigSize(NamedTuple):
    """
    A named tuple to hold figure size information to be used with matplotlib.
    """

    width: float
    height: float

    def scale(self, scalar: int | float | Fraction) -> "FigSize":
        """
        Convenience method to scale the figure size by a scalar value.

        Arguments:
            scalar: The scalar value to scale the figure size by.
        Returns:
            A new `FigSize` instance with the scaled width and height.
        Raises:
            TypeError: If the scalar is not an integer, float, or Fraction.
        """
        if not isinstance(scalar, (int, float, Fraction)):
            raise TypeError("Scalar must be a Fraction, a float, or an integer.")
        return FigSize(self.width * scalar, self.height * scalar)


@dataclass(frozen=True, eq=False)
class FigureScale(Sequence):
    """
    Class to hold figure scale information.

    This class implements the Sequence interface, allowing it to be used as a tuple-like object.
    It can be used to seamlessly set the `figure.figsize` parameter in matplotlib.

    The initialization accepts its units, besides two of the following three parameters:

    - width: The width of the figure in the specified units.
    - height: The height of the figure in the specified units.
    - aspect: The aspect ratio of the figure (width / height).

    The missing parameter will be computed based on the provided ones.

    It is set as a frozen dataclass to ensure constancy and immutability of the figure scale after creation.
    See the :obj:`FigureScale.replace` method for a way to create a new instance with modified attributes.

    Examples:
        See the :ref:`User Guide<Figure Size>` for examples of how to use this class.
    """

    units: str = "in"
    width: float | int | None = None
    height: float | int | None = None
    aspect: float | int | None = None

    _figsize: FigSize = field(init=False, repr=False, hash=False)
    _conversion_table: UnitConversionMapping = field(init=False, repr=False, hash=False)

    def __post_init__(self):
        """Compute additional internal values."""
        object.__setattr__(self, "_conversion_table", UnitConversionMapping())
        figsize = self._compute_figsize()
        object.__setattr__(self, "_figsize", figsize)

    @contextmanager
    def __call__(self, **kwargs) -> Iterator[None]:
        """
        A context manager to set the figure size in matplotlib locally on your code.

        This also enable it to be used as a decorator.
        """
        with rc_context({"figure.figsize": self, **kwargs}):
            yield

    def __eq__(self, other: object) -> bool:
        """Compare the figure scale with another object by delegating to the internal :obj:`FigSize`."""
        if isinstance(other, FigureScale):
            return self._figsize == other._figsize
        return self._figsize == other

    def __getitem__(self, index: slice | int):
        """Get items for sequence-like access by delegating to the internal :obj:`FigSize`."""
        return self._figsize[index]

    def __len__(self) -> int:
        """Get the length for sequence-like access by delegating to the internal :obj:`FigSize`."""
        return len(self._figsize)

    def _compute_figsize(self) -> FigSize:
        self._validate_attributes()
        factor = self._conversion_table[self.units]

        try:
            width_abs = self.width or self.height / self.aspect  # type: ignore
            height_abs = self.height or self.width * self.aspect  # type: ignore
        except TypeError as err:
            raise ValueError("Either width or height must be provided.") from err

        return FigSize(float(width_abs * factor), float(height_abs * factor))

    def _resize(self, new_units: str) -> FigSize:
        scale_factor = self._conversion_table["in"] / self._conversion_table[new_units]
        return self._figsize.scale(scale_factor)

    def _validate_attributes(self):
        attributes = (self.width, self.height, self.aspect)
        if sum(1 for v in attributes if v is not None) != 2:
            raise ValueError(
                "Exactly two out of width, height and aspect must be provided."
            )

        if any(v <= 0.0 for v in attributes if v is not None):
            raise ValueError(
                "The figure size must be positive, please check your inputs."
            )

    def replace(self, **kwargs) -> FigureScale:
        """Replace the attributes of the figure scale."""
        if "units" in kwargs and kwargs["units"] != self.units:
            new_figsize = self._resize(new_units=kwargs["units"])
            if self.width is not None and "width" not in kwargs:
                kwargs["width"] = new_figsize.width
            if self.height is not None and "height" not in kwargs:
                kwargs["height"] = new_figsize.height
        return cast(FigureScale, replace(self, **kwargs))

    def set_as_default(self):
        """Set the figure scale as the default on matplotlib."""
        rcParams["figure.figsize"] = self
