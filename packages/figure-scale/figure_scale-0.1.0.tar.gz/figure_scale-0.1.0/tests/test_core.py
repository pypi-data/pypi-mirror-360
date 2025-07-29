"""Test the core module."""

from contextlib import contextmanager
from fractions import Fraction
from itertools import product
from math import isclose
from unittest.mock import patch

import matplotlib.pyplot as plt
import pytest

from figure_scale.core import FigSize, FigureScale
from figure_scale.unit_conversion import INITIAL_VALUES


@contextmanager
def close_figure(fig):
    """Ensure figure is closed after use."""
    try:
        yield
    finally:
        plt.close(fig)


class TestFigSize:
    figsize = FigSize(10.0, 10.0)

    def test_fig_size_on_figure(self):
        """Test that the figure scale works on a figure."""
        fig, _ = plt.subplots(figsize=self.figsize)
        with close_figure(fig):
            actual_size = tuple(fig.get_size_inches())
            assert actual_size == self.figsize

    def test_fig_size_on_config(self):
        """Test that the figure scale works on a figure."""
        with plt.rc_context({"figure.figsize": self.figsize}):
            fig, _ = plt.subplots()
            with close_figure(fig):
                actual_size = tuple(fig.get_size_inches())
                assert actual_size == self.figsize

    @pytest.mark.parametrize("scale", [0.5, 2.0, 1, Fraction(1, 2)])
    def test_fig_size_scale(self, scale):
        """Test that the figure scale works on a figure."""
        new_figsize = self.figsize.scale(scale)
        assert new_figsize == tuple(v * scale for v in self.figsize)

    @pytest.mark.parametrize("scale", ["foo", None])
    def test_fig_size_scale__invalid(self, scale):
        """Test that the figure scale works on a figure."""
        with pytest.raises(TypeError, match="Scalar must be a"):
            self.figsize.scale(scale)


class TestFigureScale:
    """Test the FigureScale class."""

    fig_scale = FigureScale(width=12.0, height=12.0)

    def test_iter(self):
        actual_size = tuple(self.fig_scale)
        assert actual_size == (12.0, 12.0)

    def test_getitem(self):
        actual_size = self.fig_scale[:]
        assert actual_size == (12.0, 12.0)

    def test_len(self):
        assert len(self.fig_scale) == 2

    def test_equality(self):
        assert FigureScale(width=1, height=1) == FigureScale(width=1, height=1)

    def test_relative_hight(self):
        fig_scale = FigureScale(width=2.0, aspect=0.5)
        assert fig_scale == (2.0, 1.0)

    def test_relative_width(self):
        fig_scale = FigureScale(height=1.0, aspect=0.5)
        assert fig_scale == (2.0, 1.0)

    def test_no_attribute_provided(self):
        with pytest.raises(ValueError, match="Exactly two out of"):
            FigureScale()

    @patch.object(FigureScale, "_validate_attributes", return_value=None)
    def test_compute_figsize_fallback(self, mock_validate_attributes):
        with pytest.raises(
            ValueError, match="Either width or height must be provided."
        ):
            FigureScale(aspect=1.0)
        mock_validate_attributes.assert_called_once()

    @pytest.mark.parametrize("attribute", ["width", "height", "aspect"])
    def test_one_attribute_provided(self, attribute):
        kwargs = {attribute: 1.0}
        with pytest.raises(ValueError, match="Exactly two out of"):
            FigureScale(**kwargs)

    def test_all_attributes_provided(self):
        with pytest.raises(ValueError, match="Exactly two out of"):
            FigureScale(width=1.0, height=1.0, aspect=1.0)

    @pytest.mark.parametrize(
        "attributes",
        [
            {"height": -1.0, "aspect": 1.0},
            {"width": -1.0, "aspect": 1.0},
            {"width": -1.0, "height": 1.0},
            {"height": 1.0, "aspect": -1.0},
            {"width": 1.0, "aspect": -1.0},
            {"width": 1.0, "height": -1.0},
        ],
    )
    def test_negative_attributes(self, attributes):
        with pytest.raises(ValueError, match="The figure size must be positive"):
            FigureScale(**attributes)

    @pytest.mark.parametrize(
        "attributes, expected_size",
        [
            ({"width": 10.0}, (10.0, 12.0)),
            ({"height": 10.0}, (12.0, 10.0)),
            ({"width": None, "aspect": 2.0}, (6.0, 12.0)),
            ({"height": None, "aspect": 2.0}, (12.0, 24.0)),
            ({"units": "ft", "width": 1.0}, (12.0, 12.0)),
            ({"units": "ft", "height": 1.0}, (12.0, 12.0)),
        ],
    )
    def test_replace(self, attributes, expected_size):
        actual_size = self.fig_scale.replace(**attributes)
        assert all(isclose(a, b) for a, b in zip(actual_size, expected_size))

    @pytest.mark.parametrize(
        "base_units, new_units",
        list(product(INITIAL_VALUES.keys(), INITIAL_VALUES.keys())),
    )
    def test_replace_with_units(self, base_units, new_units):
        fig_scale = FigureScale(width=1.0, height=1.0, units=base_units)
        new_fig_scale = fig_scale.replace(units=new_units)
        assert all(isclose(a, b) for a, b in zip(fig_scale, new_fig_scale))

    def test_invalid_units(self):
        with pytest.raises(KeyError):
            FigureScale(width=1.0, height=1.0, units="invalid")

    @pytest.mark.parametrize("units", INITIAL_VALUES.keys())
    def test_units_conversion(self, units):
        fig_scale = FigureScale(width=1.0, height=1.0, units=units)
        factor = INITIAL_VALUES[units]
        expected_size = (1.0 * factor, 1.0 * factor)
        assert fig_scale == expected_size

    def test_used_on_figure(self):
        fig, _ = plt.subplots(figsize=self.fig_scale)
        with close_figure(fig):
            actual_size = tuple(fig.get_size_inches())
            assert actual_size == self.fig_scale

    def test_used_on_config(self):
        with plt.rc_context({"figure.figsize": self.fig_scale}):
            fig, _ = plt.subplots()
            with close_figure(fig):
                actual_size = tuple(fig.get_size_inches())
                assert actual_size == self.fig_scale

    def test_used_on_context(self):
        with self.fig_scale():
            fig, _ = plt.subplots()
            with close_figure(fig):
                actual_size = tuple(fig.get_size_inches())
                assert actual_size == self.fig_scale

    def test_used_on_decorator(self):
        @self.fig_scale()
        def dummy_plot_function():
            fig, _ = plt.subplots()
            return fig

        fig = dummy_plot_function()
        with close_figure(fig):
            actual_size = tuple(fig.get_size_inches())
            assert actual_size == self.fig_scale

    def test_set_as_default(self):
        with plt.rc_context():
            self.fig_scale.set_as_default()
            assert tuple(plt.rcParams["figure.figsize"]) == self.fig_scale
