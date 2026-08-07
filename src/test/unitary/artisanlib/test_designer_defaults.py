"""Tests for the standalone designer's factory landmarks.

These are no longer textbook coffee numbers: they are this roastery's measured
medians, taken from the 46 recorded .alog roasts with both CHARGE and DROP
marked. The tests pin the properties that make a default set usable -- ordering,
monotonic BT, and correct conversion -- rather than the exact figures, which are
allowed to be re-derived from new data.
"""

from __future__ import annotations

import pytest

from artisanlib.designer import c_delta_to, f_to

ORDER = ['CHARGE', 'DRY_END', 'FC_START', 'FC_END', 'SC_START', 'SC_END', 'DROP']

# The measured medians the defaults encode (Fahrenheit, as logged).
MEASURED_F = {
    'CHARGE': (0, 180.0),
    'DRY_END': (300, 200.0),
    'FC_START': (570, 230.0),
    'FC_END': (675, 243.0),
    'SC_START': (750, 282.0),
    'SC_END': (870, 300.0),
    'DROP': (1320, 331.0),
}


def build_defaults(unit: str) -> dict:
    """Mirror of DesignerData's factory table, without needing a QApplication."""
    def et(bt: float) -> float:
        return round(bt + c_delta_to(-50.0, unit), 1)
    return {name: {'time': t, 'BT': f_to(bt, unit), 'ET': et(f_to(bt, unit))}
            for name, (t, bt) in MEASURED_F.items()}


# -- Fahrenheit conversion -------------------------------------------------


def test_fahrenheit_is_identity_in_f() -> None:
    assert f_to(331.0, 'F') == 331.0


def test_fahrenheit_converts_to_celsius() -> None:
    assert f_to(212.0, 'C') == 100.0
    assert f_to(32.0, 'C') == 0.0


def test_f_to_and_c_to_are_inverses() -> None:
    from artisanlib.designer import c_to
    assert abs(f_to(c_to(150.0, 'F'), 'C') - 150.0) < 0.1


# -- ordering and shape ----------------------------------------------------


@pytest.mark.parametrize('unit', ['C', 'F'])
def test_times_strictly_ascend(unit: str) -> None:
    """apply_landmark_changes refuses a non-ascending set; the defaults must pass it."""
    d = build_defaults(unit)
    times = [d[n]['time'] for n in ORDER]
    assert times == sorted(times)
    assert len(set(times)) == len(times)


@pytest.mark.parametrize('unit', ['C', 'F'])
def test_bt_rises_monotonically(unit: str) -> None:
    d = build_defaults(unit)
    bts = [d[n]['BT'] for n in ORDER]
    assert bts == sorted(bts), bts


def test_charge_is_time_zero() -> None:
    assert build_defaults('F')['CHARGE']['time'] == 0


def test_drop_describes_the_roast_actually_done_here() -> None:
    """22 minutes, not the 11-minute coffee roast the old defaults described."""
    assert build_defaults('F')['DROP']['time'] == 1320


def test_drop_temperature_matches_the_roast_log() -> None:
    """Log records 341-362 F end temp; the profile median is 331 F at DROP."""
    assert build_defaults('F')['DROP']['BT'] == 331.0


# -- ET derivation ---------------------------------------------------------


@pytest.mark.parametrize('unit', ['C', 'F'])
def test_et_sits_one_offset_below_bt(unit: str) -> None:
    d = build_defaults(unit)
    offset = c_delta_to(-50.0, unit)
    for name in ORDER:
        assert abs((d[name]['ET'] - d[name]['BT']) - offset) < 0.05, name


def test_et_gap_is_ninety_in_fahrenheit() -> None:
    d = build_defaults('F')
    assert d['DROP']['BT'] - d['DROP']['ET'] == 90.0


def test_et_gap_is_fifty_in_celsius() -> None:
    d = build_defaults('C')
    assert abs((d['DROP']['BT'] - d['DROP']['ET']) - 50.0) < 0.05


# -- unit independence -----------------------------------------------------


def test_same_roast_in_either_unit() -> None:
    """Switching unit must not change the physical roast being described."""
    f, c = build_defaults('F'), build_defaults('C')
    for name in ORDER:
        assert f[name]['time'] == c[name]['time']
        assert abs(f_to(f[name]['BT'], 'C') - c[name]['BT']) < 0.15, name
