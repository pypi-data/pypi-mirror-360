"""Test the unit conversion table."""

from collections import UserDict
from decimal import Decimal
from fractions import Fraction

import pint
import pytest

from figure_scale.unit_conversion import INITIAL_VALUES, UnitConversionMapping


@pytest.mark.parametrize("unit", INITIAL_VALUES)
class TestInitialValues:
    ureg = pint.UnitRegistry()

    def test_value_is_positive(self, unit):
        assert INITIAL_VALUES[unit] > 0.0

    def test_key_is_string(self, unit):
        assert isinstance(unit, str)

    def test_conversion_to_inches(self, unit):
        actual_value = INITIAL_VALUES[unit]
        if unit == "pt":
            # This is not covered by pint
            expected_value = 1.0 / 72.0
        else:
            expected_value = self.ureg(unit).to("in").magnitude
        assert actual_value == pytest.approx(expected_value)


class TestUnitConversionMapping:
    unit_conversion_mapping = UnitConversionMapping()

    def test_singleton(self):
        unit_conversion_1 = UnitConversionMapping()
        unit_conversion_2 = UnitConversionMapping()
        assert unit_conversion_1 is unit_conversion_2

    def test_unit_conversion_is_user_dict(self):
        assert isinstance(self.unit_conversion_mapping, UserDict)

    def test_initial_values(self):
        expected_values = {
            key: Fraction(value) for key, value in INITIAL_VALUES.items()
        }
        assert self.unit_conversion_mapping == expected_values

    def test_set_negative_value__value_error(self):
        with pytest.raises(
            ValueError, match="All values must be positive non-zero numbers"
        ):
            self.unit_conversion_mapping["foo"] = -1.0

    @pytest.mark.parametrize("key", [0, False, 0.0, b"foo", None])
    def test_set_non_string_key__type_error(self, key):
        with pytest.raises(TypeError, match="All keys must be strings"):
            self.unit_conversion_mapping[key] = 1.0
        assert key not in self.unit_conversion_mapping

    @pytest.mark.parametrize("value", ["foo", None])
    def test_set_invalid_fraction__value_error(self, value):
        with pytest.raises(
            ValueError, match="The provided value can not be converted to a fraction"
        ):
            self.unit_conversion_mapping["foo"] = value
        assert "foo" not in self.unit_conversion_mapping

    @pytest.mark.parametrize("value", [1, 1.0, "1/2", Fraction(1, 2), Decimal(0.5)])
    def test_set__success(self, value):
        try:
            self.unit_conversion_mapping["foo"] = value
            assert self.unit_conversion_mapping["foo"] == Fraction(value)
        finally:
            self.unit_conversion_mapping.pop("foo", None)
