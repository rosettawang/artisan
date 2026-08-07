"""Tests for the machine rules now living in DesignerData.

Every rule here corresponds to a mistake actually made on this roaster, not to a
general principle about roasting. They were previously encoded only in
make_roast_curve.py, which meant they protected exactly one of the two tools that
produce curves. In the model they protect the GUI, the CLI and the script.
"""

from __future__ import annotations

import pytest

from artisanlib.designer import (AUTO_HEAT_CUTOFF_F, DEFAULT_TAIL_MINUTES,
                                 ROR_CEILING_F_PER_MIN, DesignerValidation, _parse_landmark)


class FakeData:
    """DesignerData's validate() only reads landmarks and temp_unit."""

    from artisanlib.designer import DesignerData as _D
    enabled_landmarks = _D.enabled_landmarks
    segment_rors = _D.segment_rors
    validate = _D.validate

    def __init__(self, rows: list[tuple[str, int, float]], unit: str = 'F') -> None:
        self.temp_unit = unit
        self.landmarks = {n: {'time': t, 'BT': bt, 'enabled': True} for n, t, bt in rows}


def declining() -> FakeData:
    """A curve this machine can actually follow."""
    return FakeData([('CHARGE', 0, 190.0), ('DRY_END', 360, 250.0),
                     ('FC_START', 780, 300.0), ('DROP', 1440, 325.0)])


# -- ordering --------------------------------------------------------------


def test_a_sane_curve_passes() -> None:
    v = declining().validate()
    assert v.ok, str(v)


def test_two_landmarks_minimum() -> None:
    v = FakeData([('CHARGE', 0, 190.0)]).validate()
    assert not v.ok
    assert 'two enabled landmarks' in v.errors[0]


def test_out_of_roast_order_is_an_error() -> None:
    """DROP at 1:00 sorts fine by time and is still nonsense as a roast."""
    d = declining()
    d.landmarks['DROP']['time'] = 60      # before DRY_END
    v = d.validate()
    assert not v.ok
    assert any('comes before it in a roast' in e for e in v.errors), v.errors


def test_two_landmarks_at_the_same_time_is_an_error() -> None:
    d = declining()
    d.landmarks['FC_START']['time'] = d.landmarks['DRY_END']['time']
    assert not d.validate().ok


# -- the declining rate of rise rule --------------------------------------


def test_rising_rate_of_rise_is_refused() -> None:
    """The rule that catches the composite-median defaults."""
    d = FakeData([('CHARGE', 0, 180.0), ('DRY_END', 300, 200.0),
                  ('FC_START', 570, 230.0), ('DROP', 1320, 331.0)])
    v = d.validate()
    assert not v.ok
    assert any('must decline' in e for e in v.errors)


def test_the_error_names_both_segments() -> None:
    d = FakeData([('CHARGE', 0, 180.0), ('DRY_END', 300, 200.0), ('DROP', 600, 260.0)])
    v = d.validate()
    msg = ' '.join(v.errors)
    assert 'CHARGE' in msg and 'DRY_END' in msg and 'DROP' in msg


def test_a_flat_rate_of_rise_is_allowed() -> None:
    """Equal segments must not trip the rising check on floating-point noise."""
    d = FakeData([('CHARGE', 0, 100.0), ('DRY_END', 600, 200.0), ('DROP', 1200, 300.0)])
    assert d.validate().ok


# -- warnings, which do not refuse ----------------------------------------


def test_above_the_ror_ceiling_warns_but_passes() -> None:
    d = FakeData([('CHARGE', 0, 190.0), ('DROP', 300, 290.0)])   # 20 deg/min
    v = d.validate()
    assert v.ok, str(v)
    assert any('sustains about' in w for w in v.warnings)


def test_at_the_ceiling_does_not_warn() -> None:
    d = FakeData([('CHARGE', 0, 190.0), ('DROP', 600, 190.0 + ROR_CEILING_F_PER_MIN * 10)])
    assert not any('sustains' in w for w in d.validate().warnings)


def test_above_the_auto_heat_cutoff_warns() -> None:
    d = declining()
    d.landmarks['DROP']['BT'] = AUTO_HEAT_CUTOFF_F + 10
    v = d.validate()
    assert v.ok
    assert any('auto-heat cutoff' in w for w in v.warnings)


def test_below_the_cutoff_does_not_warn() -> None:
    assert not any('auto-heat' in w for w in declining().validate().warnings)


def test_no_tail_warns() -> None:
    """pidOffDROP kills the burner at DROP; a curve ending there leaves Follow with no setpoint."""
    v = declining().validate(tail_minutes=0)
    assert v.ok
    assert any('coasts' in w for w in v.warnings)


def test_default_tail_does_not_warn() -> None:
    assert not any('coasts' in w for w in declining().validate().warnings)


def test_default_tail_is_positive() -> None:
    assert DEFAULT_TAIL_MINUTES > 0


# -- disabled landmarks ----------------------------------------------------


def test_disabled_landmarks_are_ignored() -> None:
    d = declining()
    d.landmarks['SC_START'] = {'time': 60, 'BT': 999.0, 'enabled': False}
    assert d.validate().ok, 'a disabled landmark must not affect validation'


# -- Celsius ---------------------------------------------------------------


def test_thresholds_convert_for_celsius() -> None:
    """A Celsius user must not be warned against Fahrenheit numbers."""
    d = FakeData([('CHARGE', 0, 88.0), ('DRY_END', 360, 121.0),
                  ('FC_START', 780, 149.0), ('DROP', 1440, 163.0)], unit='C')
    v = d.validate()
    assert v.ok, str(v)
    assert not v.warnings, v.warnings   # 163 C is below the 166 C cutoff


def test_celsius_cutoff_still_fires_when_exceeded() -> None:
    d = FakeData([('CHARGE', 0, 88.0), ('DROP', 1440, 200.0)], unit='C')
    assert any('auto-heat' in w for w in d.validate().warnings)


# -- the result object -----------------------------------------------------


def test_result_is_falsy_only_on_errors() -> None:
    v = DesignerValidation()
    assert v.ok
    v.warnings.append('something')
    assert v.ok
    v.errors.append('something')
    assert not v.ok


def test_result_renders_both_kinds() -> None:
    v = DesignerValidation()
    v.errors.append('bad'); v.warnings.append('iffy')
    text = str(v)
    assert 'ERROR: bad' in text and 'warning: iffy' in text


def test_clean_result_says_so() -> None:
    assert 'sane' in str(DesignerValidation())


# -- CLI landmark parsing --------------------------------------------------


@pytest.mark.parametrize(('text', 'expected'), [
    ('DROP=24:00@340', ('DROP', 1440.0, 340.0)),
    ('drop=24:00@340', ('DROP', 1440.0, 340.0)),
    ('CHARGE=0:00@190.5', ('CHARGE', 0.0, 190.5)),
    (' DRY_END = 6:00 @ 250 ', ('DRY_END', 360.0, 250.0)),
])
def test_landmark_spec_parses(text: str, expected: tuple) -> None:
    assert _parse_landmark(text) == expected


@pytest.mark.parametrize('text', ['DROP', 'DROP=24:00', '24:00@340', 'DROP=banana@340',
                                  'DROP=24:00@banana'])
def test_bad_landmark_spec_rejected(text: str) -> None:
    with pytest.raises(ValueError):
        _parse_landmark(text)
