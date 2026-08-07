"""Tests for recording background nudges.

Moving the background is the roaster stating, in seconds, how wrong the plan
was. Artisan accumulated the total and discarded it; these cover the record that
now survives, and the warning that fires when the nudge moved a live setpoint.

The methods only touch attributes on `self`, so they are exercised unbound
against a stub -- no Qt, no canvas, no roast.
"""

from __future__ import annotations

from typing import Any

import pytest
from PyQt6.QtWidgets import QApplication

# canvas.py reads QApplication.instance().artisanviewerMode at import time -- it
# expects Artisan's own QApplication subclass. A plain one plus that attribute is
# enough to import the module. Reuse an existing instance if a test made one.
_app = QApplication.instance() or QApplication([])
if not hasattr(_app, 'artisanviewerMode'):
    _app.artisanviewerMode = False  # type: ignore[attr-defined]

from artisanlib.canvas import tgraphcanvas  # noqa: E402

record = tgraphcanvas.recordBackgroundNudge
following = tgraphcanvas.pidActiveFollowingBackground


class StubPID:
    def __init__(self, active: bool = False, svMode: int = 0) -> None:
        self.pidActive = active
        self.svMode = svMode


class StubAW:
    def __init__(self, pidcontrol: Any = None) -> None:
        self.pidcontrol = pidcontrol
        self.messages: list[str] = []

    def sendmessage(self, msg: str) -> None:
        self.messages.append(msg)


class StubQmc:
    """Just the attributes recordBackgroundNudge reads."""

    def __init__(self, *, timex: list[float] | None = None, temp2: list[float] | None = None,
                 charge_idx: int = -1, moved_x: int = 0, pidcontrol: Any = None) -> None:
        self.timex = timex if timex is not None else []
        self.temp2 = temp2 if temp2 is not None else []
        self.timeindex = [charge_idx, 0, 0, 0, 0, 0, 0, 0]
        self.backgroundprofile_moved_x = moved_x
        self.background_nudges: list[dict[str, Any]] = []
        self.aw = StubAW(pidcontrol)

    # recordBackgroundNudge calls this on self, so bind the real implementation
    pidActiveFollowingBackground = tgraphcanvas.pidActiveFollowingBackground


# -- the record ------------------------------------------------------------


def test_a_nudge_is_recorded() -> None:
    q = StubQmc()
    record(q, 'right', 50)
    assert len(q.background_nudges) == 1
    assert q.background_nudges[0]['direction'] == 'right'
    assert q.background_nudges[0]['step'] == 50


def test_nudges_accumulate_in_order() -> None:
    q = StubQmc()
    record(q, 'right', 50)
    record(q, 'left', 30)
    record(q, 'up', 10)
    assert [n['direction'] for n in q.background_nudges] == ['right', 'left', 'up']


def test_time_is_relative_to_charge() -> None:
    """The useful question is 'when in the roast', not wall clock."""
    q = StubQmc(timex=[100.0, 160.0, 340.0], charge_idx=0)
    record(q, 'right', 50)
    assert q.background_nudges[0]['t'] == 240.0


def test_time_is_none_before_charge() -> None:
    q = StubQmc(timex=[10.0, 20.0], charge_idx=-1)
    record(q, 'right', 50)
    assert q.background_nudges[0]['t'] is None


def test_bt_at_the_moment_is_captured() -> None:
    q = StubQmc(timex=[0.0, 60.0], temp2=[180.0, 214.5], charge_idx=0)
    record(q, 'left', 50)
    assert q.background_nudges[0]['BT'] == 214.5


def test_bt_none_when_no_reading() -> None:
    """-1 is Artisan's 'no reading' sentinel and must not be logged as a temperature."""
    q = StubQmc(timex=[0.0], temp2=[-1], charge_idx=0)
    record(q, 'left', 50)
    assert q.background_nudges[0]['BT'] is None


def test_empty_channels_do_not_raise() -> None:
    record(StubQmc(), 'down', 5)  # must not raise


def test_recording_never_propagates_an_error() -> None:
    """A logging failure must never take down a nudge mid-roast."""
    q = StubQmc()
    q.background_nudges = None  # type: ignore[assignment]  # .append will raise
    record(q, 'left', 50)  # swallowed, not raised


# -- the PID-follow warning ------------------------------------------------


def test_no_warning_when_pid_is_off() -> None:
    q = StubQmc(pidcontrol=StubPID(active=False, svMode=2))
    record(q, 'left', 50)
    assert q.aw.messages == []


def test_no_warning_when_pid_is_not_following_background() -> None:
    """svMode 0 is manual, 1 is Ramp/Soak -- neither reads the background."""
    q = StubQmc(pidcontrol=StubPID(active=True, svMode=1))
    record(q, 'left', 50)
    assert q.aw.messages == []


def test_warns_when_the_nudge_moved_a_live_setpoint() -> None:
    q = StubQmc(moved_x=-50, pidcontrol=StubPID(active=True, svMode=2))
    record(q, 'left', 50)
    assert len(q.aw.messages) == 1
    assert 'setpoint' in q.aw.messages[0]


def test_warning_states_the_cumulative_offset() -> None:
    q = StubQmc(moved_x=-120, pidcontrol=StubPID(active=True, svMode=2))
    record(q, 'left', 50)
    assert '-120' in q.aw.messages[0]


@pytest.mark.parametrize('direction', ['up', 'down'])
def test_vertical_nudges_do_not_warn(direction: str) -> None:
    """Only left/right shift the time axis the setpoint is read from."""
    q = StubQmc(pidcontrol=StubPID(active=True, svMode=2))
    record(q, direction, 5)
    assert q.aw.messages == []


def test_vertical_nudges_are_still_recorded() -> None:
    q = StubQmc(pidcontrol=StubPID(active=True, svMode=2))
    record(q, 'up', 5)
    assert len(q.background_nudges) == 1


# -- the follow predicate --------------------------------------------------


@pytest.mark.parametrize(('active', 'sv_mode', 'expected'), [
    (True, 2, True),
    (True, 1, False),
    (True, 0, False),
    (False, 2, False),
])
def test_follow_predicate(active: bool, sv_mode: int, expected: bool) -> None:
    assert following(StubQmc(pidcontrol=StubPID(active, sv_mode))) is expected


def test_follow_predicate_without_a_pid_controller() -> None:
    assert following(StubQmc(pidcontrol=None)) is False
