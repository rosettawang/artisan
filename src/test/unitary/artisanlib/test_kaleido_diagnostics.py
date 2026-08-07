"""Tests for the Kaleido serial error diagnosis.

The EINVAL case is the one that matters and the one that actually happened: a
CP210x adapter wedged such that every tcsetattr failed with errno 22, including
writing back identical attributes. The generic error message sent the operator
to check baud rates; the real fix was unplugging the cable.
"""

from __future__ import annotations

import termios

import pytest

from artisanlib.kaleido import diagnose_serial_error


def test_termios_einval_is_recognised() -> None:
    """termios.error carries (errno, msg) in args and has no .errno attribute."""
    e = termios.error(22, 'Invalid argument')
    remedy = diagnose_serial_error(e)
    assert remedy is not None
    assert 'EINVAL' in remedy
    assert 'nplug' in remedy  # "Unplug"/"unplug"


def test_oserror_einval_is_recognised() -> None:
    e = OSError(22, 'Invalid argument')
    remedy = diagnose_serial_error(e)
    assert remedy is not None and 'EINVAL' in remedy


def test_einval_recognised_from_message_alone() -> None:
    """pyserial sometimes wraps the cause in SerialException with no errno."""
    class SerialException(Exception):
        pass

    remedy = diagnose_serial_error(SerialException("could not open port: (22, 'Invalid argument')"))
    assert remedy is not None and 'EINVAL' in remedy


def test_einval_says_it_is_not_a_settings_problem() -> None:
    """The whole point: stop people re-checking baud rate and port name."""
    remedy = diagnose_serial_error(OSError(22, 'Invalid argument'))
    assert remedy is not None
    assert 'not a baud rate' in remedy


def test_missing_port() -> None:
    remedy = diagnose_serial_error(OSError(2, 'No such file or directory'))
    assert remedy is not None and 'does not exist' in remedy


def test_port_busy_names_the_one_owner_rule() -> None:
    remedy = diagnose_serial_error(OSError(16, 'Resource busy'))
    assert remedy is not None and 'one program' in remedy


def test_permission_denied() -> None:
    remedy = diagnose_serial_error(OSError(13, 'Permission denied'))
    assert remedy is not None and 'permission' in remedy


@pytest.mark.parametrize('exc', [
    TimeoutError('timed out'),
    ValueError('something else entirely'),
    OSError(9, 'Bad file descriptor'),
])
def test_unknown_errors_return_none(exc: BaseException) -> None:
    """No remedy invented for cases we have not actually diagnosed."""
    assert diagnose_serial_error(exc) is None


def test_bare_exception_with_no_args_does_not_raise() -> None:
    assert diagnose_serial_error(Exception()) is None


def test_non_int_first_arg_does_not_confuse_errno_extraction() -> None:
    assert diagnose_serial_error(Exception('Bad file descriptor')) is None
