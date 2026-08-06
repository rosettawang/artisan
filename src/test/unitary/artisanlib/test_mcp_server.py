"""Unit tests for the read-only MCP server (Phase A).

Exercises the state readers against a stub ApplicationWindow, so none of this
needs Qt, a running Artisan, or a roaster.
"""

from __future__ import annotations

from typing import Any

import pytest

from artisanlib.mcp_server import MILESTONES, ArtisanMCP, _f


class StubQmc:
    def __init__(self, **kw: Any) -> None:
        self.mode = kw.get('mode', 'F')
        self.flagon = kw.get('flagon', True)
        self.flagstart = kw.get('flagstart', True)
        self.timex = kw.get('timex', [])
        self.temp1 = kw.get('temp1', [])
        self.temp2 = kw.get('temp2', [])
        self.timeindex = kw.get('timeindex', [-1, 0, 0, 0, 0, 0, 0, 0])


class StubKaleido:
    def getHeaterFan(self) -> tuple[float, float]:
        return 55.0, 60.0

    def getDrumAH(self) -> tuple[float, float]:
        return 40.0, 0.0

    def getSVAT(self) -> tuple[float, float]:
        return 0.0, 71.2


class StubAW:
    def __init__(self, qmc: StubQmc, kaleido: Any = None) -> None:
        self.qmc = qmc
        self.kaleido = kaleido


def make(**kw: Any) -> ArtisanMCP:
    return ArtisanMCP(StubAW(StubQmc(**kw), kw.pop('kaleido', None)))  # type: ignore[arg-type]


# -- helpers ---------------------------------------------------------------


def test_f_rejects_artisan_no_reading_sentinel() -> None:
    assert _f(-1) is None
    assert _f(-1.0) is None
    assert _f(210.5) == 210.5
    assert _f(None) is None
    assert _f('210') is None
    assert _f(True) is None  # bool is an int subclass; must not become 1.0


# -- elapsed ---------------------------------------------------------------


def test_elapsed_is_none_before_charge() -> None:
    assert make(timex=[0.0, 1.0, 2.0]).elapsed() is None


def test_elapsed_counts_from_charge() -> None:
    mcp = make(timex=[0.0, 30.0, 90.0], timeindex=[1, 0, 0, 0, 0, 0, 0, 0])
    assert mcp.elapsed() == 60.0


def test_elapsed_survives_out_of_range_index() -> None:
    mcp = make(timex=[0.0], timeindex=[99, 0, 0, 0, 0, 0, 0, 0])
    assert mcp.elapsed() is None


# -- milestones ------------------------------------------------------------


def test_no_milestones_when_nothing_marked() -> None:
    assert make(timex=[0.0, 1.0], temp2=[20.0, 21.0]).milestones() == {}


def test_charge_and_dry_end_reported_with_offsets() -> None:
    mcp = make(
        timex=[0.0, 10.0, 250.0, 300.0],
        temp2=[200.0, 90.0, 150.0, 165.0],
        timeindex=[1, 2, 0, 0, 0, 0, 0, 0],
    )
    ms = mcp.milestones()
    assert set(ms) == {'CHARGE', 'DRY_END'}
    assert ms['CHARGE']['seconds_after_charge'] == 0.0
    assert ms['DRY_END']['seconds_after_charge'] == 240.0
    assert ms['DRY_END']['mm:ss'] == '4:00'
    assert ms['DRY_END']['BT'] == 150.0


def test_slot_zero_sentinel_differs_from_the_others() -> None:
    """CHARGE unset is -1; every other slot unset is 0. Index 0 is a real index."""
    mcp = make(timex=[5.0, 6.0], temp2=[100.0, 101.0],
               timeindex=[0, 0, 0, 0, 0, 0, 0, 0])
    ms = mcp.milestones()
    assert 'CHARGE' in ms          # index 0 is legitimate for CHARGE
    assert 'DRY_END' not in ms     # index 0 means unset for the rest


def test_milestone_names_match_artisan_order() -> None:
    assert MILESTONES[0] == 'CHARGE'
    assert MILESTONES[6] == 'DROP'
    assert len(MILESTONES) == 8


# -- rate of rise ----------------------------------------------------------


def test_ror_none_without_enough_samples() -> None:
    assert make(timex=[0.0], temp2=[100.0]).ror() is None


def test_ror_none_when_window_not_covered() -> None:
    assert make(timex=[0.0, 5.0], temp2=[100.0, 110.0]).ror() is None


def test_ror_degrees_per_minute() -> None:
    # +15 degrees over 30s = 30 deg/min
    mcp = make(timex=[0.0, 30.0], temp2=[100.0, 115.0])
    assert mcp.ror(window=30.0) == 30.0


def test_ror_negative_while_falling() -> None:
    mcp = make(timex=[0.0, 60.0], temp2=[200.0, 180.0])
    assert mcp.ror(window=30.0) == -20.0


def test_ror_none_when_reading_is_the_sentinel() -> None:
    assert make(timex=[0.0, 30.0], temp2=[100.0, -1]).ror() is None


# -- machine ---------------------------------------------------------------


def test_machine_reports_absent_driver() -> None:
    m = make().machine()
    assert m['connected'] is False


def test_machine_reads_actuators() -> None:
    mcp = ArtisanMCP(StubAW(StubQmc(), StubKaleido()))  # type: ignore[arg-type]
    m = mcp.machine()
    assert m['connected'] is True
    assert m['heater_pct'] == 55.0
    assert m['fan_pct'] == 60.0
    assert m['drum_pct'] == 40.0
    assert m['machine_pid_on'] is False


def test_machine_says_heater_state_is_unconfirmed() -> None:
    mcp = ArtisanMCP(StubAW(StubQmc(), StubKaleido()))  # type: ignore[arg-type]
    assert 'COMMANDED' in mcp.machine()['heater_state_note']


def test_machine_survives_a_driver_that_raises() -> None:
    class Broken:
        def getHeaterFan(self) -> tuple[float, float]:
            raise RuntimeError('serial gone')

        def getDrumAH(self) -> tuple[float, float]:
            raise RuntimeError('serial gone')

        def getSVAT(self) -> tuple[float, float]:
            raise RuntimeError('serial gone')

    mcp = ArtisanMCP(StubAW(StubQmc(), Broken()))  # type: ignore[arg-type]
    m = mcp.machine()
    assert m['connected'] is True
    assert 'heater_pct' not in m


# -- status ----------------------------------------------------------------


def test_status_is_declared_read_only() -> None:
    assert make().status()['read_only'] is True


def test_status_unit_comes_from_artisan_not_the_machine() -> None:
    s = make(mode='C').status()
    assert s['unit'] == 'C'
    assert 'qmc.mode' in s['unit_source']


def test_status_reports_bt_and_et_from_the_right_channels() -> None:
    # Artisan convention: temp1 is ET, temp2 is BT.
    s = make(timex=[0.0, 1.0], temp1=[300.0, 310.0], temp2=[200.0, 205.0]).status()
    assert s['BT'] == 205.0
    assert s['ET'] == 310.0


def test_status_handles_an_empty_profile() -> None:
    s = make().status()
    assert s['BT'] is None and s['ET'] is None and s['samples'] == 0
    assert s['ok'] is True


def test_status_ragged_channels_do_not_index_error() -> None:
    s = make(timex=[0.0, 1.0, 2.0], temp1=[300.0], temp2=[200.0, 205.0]).status()
    assert s['samples'] == 1


@pytest.mark.parametrize('flag', ['sampling', 'recording'])
def test_status_exposes_run_flags(flag: str) -> None:
    assert make(flagon=True, flagstart=True).status()[flag] is True


def test_not_running_before_start() -> None:
    assert make().running is False
