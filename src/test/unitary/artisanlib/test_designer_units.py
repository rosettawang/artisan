"""Tests for the standalone designer's temperature-unit handling.

The bug these pin: everything in the standalone designer was hardcoded to
Celsius -- labels, axis, defaults and the BT-only ET offset -- while the owner
roasts in Fahrenheit. Fahrenheit numbers were being typed into fields captioned
(deg C).

The subtle half is that an *offset* is an interval, so it converts by the ratio
alone. Converting -50 with the absolute formula would give -58, which is wrong
in a way that looks plausible.
"""

from __future__ import annotations

import pytest

from artisanlib.designer import c_delta_to, c_to, designer_temp_unit


# -- absolute conversions --------------------------------------------------


def test_celsius_is_identity() -> None:
    assert c_to(150.0, 'C') == 150.0
    assert c_to(-40.0, 'C') == -40.0


@pytest.mark.parametrize(('celsius', 'fahrenheit'), [
    (0.0, 32.0),
    (100.0, 212.0),
    (-40.0, -40.0),      # the crossover point
    (80.0, 176.0),       # designer CHARGE default
    (210.0, 410.0),      # designer DROP default
])
def test_absolute_conversion(celsius: float, fahrenheit: float) -> None:
    assert c_to(celsius, 'F') == fahrenheit


# -- interval conversions --------------------------------------------------


def test_interval_celsius_is_identity() -> None:
    assert c_delta_to(-50.0, 'C') == -50.0


def test_interval_conversion_has_no_offset_term() -> None:
    """-50 C of *gap* is -90 F of gap, not -58."""
    assert c_delta_to(-50.0, 'F') == -90.0


def test_interval_is_not_the_absolute_formula() -> None:
    assert c_delta_to(-50.0, 'F') != c_to(-50.0, 'F')


def test_zero_interval_stays_zero() -> None:
    """An absolute conversion would turn a zero gap into 32 degrees."""
    assert c_delta_to(0.0, 'F') == 0.0


# -- unit detection --------------------------------------------------------


class StubSettings:
    def __init__(self, mode: object) -> None:
        self._mode = mode

    def value(self, key: str, default: object = None) -> object:
        return self._mode if key == 'Mode' else default


@pytest.mark.parametrize(('stored', 'expected'), [
    ('F', 'F'),
    ('f', 'F'),
    ('Fahrenheit', 'F'),
    ('C', 'C'),
    ('c', 'C'),
    ('Celsius', 'C'),
])
def test_unit_read_from_artisan_settings(monkeypatch: pytest.MonkeyPatch,
                                         stored: str, expected: str) -> None:
    monkeypatch.setattr('artisanlib.designer.QSettings',
                        lambda *a, **k: StubSettings(stored))
    assert designer_temp_unit() == expected


def test_unit_defaults_to_celsius_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr('artisanlib.designer.QSettings',
                        lambda *a, **k: StubSettings(None))
    assert designer_temp_unit() == 'C'


def test_unit_defaults_to_celsius_when_settings_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """A standalone launch must never crash over a settings lookup."""
    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError('no settings here')

    monkeypatch.setattr('artisanlib.designer.QSettings', boom)
    assert designer_temp_unit() == 'C'


# -- strict time parsing ---------------------------------------------------
#
# stringtoseconds_standalone() returns 0.0 for unparseable input. That is fine
# for its callers but useless for validation: "banana" became 0:00 and the
# operator was told the landmark was out of order -- true, but not the fault.


@pytest.mark.parametrize(('text', 'seconds'), [
    ('0:00', 0.0),
    ('5:00', 300.0),
    ('22:00', 1320.0),
    ('9:30', 570.0),
    ('12', 12.0),        # bare number is seconds
    ('5: 30', 330.0),    # tolerate stray space
])
def test_strict_parse_accepts(text: str, seconds: float) -> None:
    from artisanlib.designer import parse_time_strict
    assert parse_time_strict(text) == seconds


@pytest.mark.parametrize('text', [
    'banana', '', '   ', '1:2:3', '-1:00', '5:99', '1.5:00', 'mm:ss',
])
def test_strict_parse_rejects(text: str) -> None:
    from artisanlib.designer import parse_time_strict
    with pytest.raises(ValueError):
        parse_time_strict(text)


def test_strict_parse_differs_from_the_lenient_one() -> None:
    """The lenient parser silently returns 0.0, which is what hid the real fault."""
    from artisanlib.designer import parse_time_strict, stringtoseconds_standalone
    assert stringtoseconds_standalone('banana') == 0.0
    with pytest.raises(ValueError):
        parse_time_strict('banana')


def test_a_25_minute_drop_parses() -> None:
    """The original complaint: anything past ~18 minutes appeared to revert."""
    from artisanlib.designer import parse_time_strict
    assert parse_time_strict('25:00') == 1500.0
