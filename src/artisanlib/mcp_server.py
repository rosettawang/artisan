#
# ABOUT
# MCP server for artisan scope -- Phase A, read only.
#
# Exposes the live roast to an MCP client (Claude) over streamable-HTTP on
# loopback. This phase deliberately has NO write path: no tool here can move the
# heater, the fan or the drum. See specs/mcp-server.html.
#
# Two things about this file are load-bearing and easy to undo by accident:
#
#   1. It reads Artisan state from a background thread. Plain attribute reads of
#      qmc lists are tolerated; ANY mutation must cross into the GUI thread by Qt
#      signal instead. Phase A mutates nothing, which is why it is safe to be the
#      first thing that runs against a real roast.
#   2. stdio is not available -- Artisan is a GUI app that owns its own stdin and
#      stdout, and nothing launches it as a subprocess. The transport has to be a
#      socket, bound to 127.0.0.1 only.
#
# The thread lifecycle is copied from artisanlib/weblcds.py (WebView.startWeb /
# stopWeb) rather than invented, so there is one pattern in the tree for "GUI app
# hosting a server on a background asyncio loop".
#
# LICENSE
# This program or module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import suppress
from threading import Thread
from typing import Any, Final, TYPE_CHECKING

if TYPE_CHECKING:
    from artisanlib.main import ApplicationWindow  # pylint: disable=unused-import

_log: Final[logging.Logger] = logging.getLogger(__name__)

# timeindex slots, in order. CHARGE is -1 when unset; the rest are 0 when unset.
MILESTONES: Final[tuple[str, ...]] = (
    'CHARGE', 'DRY_END', 'FC_START', 'FC_END', 'SC_START', 'SC_END', 'DROP', 'COOL')

DEFAULT_HOST: Final[str] = '127.0.0.1'
DEFAULT_PORT: Final[int] = 8770

INSTRUCTIONS: Final[str] = """\
Read-only view of a live coffee roast in Artisan.

There is no write path in this build: nothing here can move the heater, fan or
drum. If asked to change the machine, say that this server cannot and that the
operator must do it at the roaster or in Artisan.

Temperatures are in the unit reported by `unit` -- the machine does not report
its own unit, so Artisan's setting is the authority. Read `roast_status` before
drawing any conclusion; values older than a couple of seconds are stale.
"""


def _f(value: Any) -> float | None:
    """Coerce to float, or None if it isn't a usable number."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        f = float(value)
        # Artisan uses -1 as "no reading yet" on several channels.
        return None if f == -1 else f
    return None


class ArtisanMCP:
    """Hosts the MCP server on its own asyncio loop in a daemon thread."""

    __slots__ = ['_aw', '_host', '_port', '_loop', '_thread', '_server', '_running']

    def __init__(self, aw: 'ApplicationWindow', host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT) -> None:
        self._aw = aw
        self._host = host
        self._port = port
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: Thread | None = None
        self._server: Any = None
        self._running: bool = False

    # -- state readers ------------------------------------------------------
    #
    # Kept as plain methods rather than closures so they can be unit-tested
    # against a stub `aw` without standing up a server.

    def elapsed(self) -> float | None:
        """Seconds since CHARGE, or None if CHARGE has not been marked."""
        qmc = self._aw.qmc
        idx = qmc.timeindex[0]
        if idx < 0 or idx >= len(qmc.timex):
            return None
        return round(qmc.timex[-1] - qmc.timex[idx], 1)

    def milestones(self) -> dict[str, Any]:
        """Marked roast milestones, each with its time relative to CHARGE."""
        qmc = self._aw.qmc
        charge_idx = qmc.timeindex[0]
        charge_t = qmc.timex[charge_idx] if 0 <= charge_idx < len(qmc.timex) else None
        out: dict[str, Any] = {}
        for slot, name in enumerate(MILESTONES):
            idx = qmc.timeindex[slot]
            # CHARGE uses -1 for unset; every other slot uses 0.
            if (slot == 0 and idx < 0) or (slot > 0 and idx == 0):
                continue
            if not 0 <= idx < len(qmc.timex):
                continue
            entry: dict[str, Any] = {'index': idx}
            if charge_t is not None:
                secs = qmc.timex[idx] - charge_t
                entry['seconds_after_charge'] = round(secs, 1)
                entry['mm:ss'] = f'{int(abs(secs) // 60):d}:{int(abs(secs) % 60):02d}'
            temp = _f(qmc.temp2[idx]) if idx < len(qmc.temp2) else None
            if temp is not None:
                entry['BT'] = temp
            out[name] = entry
        return out

    def ror(self, window: float = 30.0) -> float | None:
        """Bean-temperature rate of rise, degrees per minute over `window` seconds.

        Computed here rather than read off qmc so it does not depend on which
        smoothing/delta settings the user has active.
        """
        qmc = self._aw.qmc
        timex, temp2 = qmc.timex, qmc.temp2
        n = min(len(timex), len(temp2))
        if n < 2:
            return None
        now_t, now_v = timex[n - 1], _f(temp2[n - 1])
        if now_v is None:
            return None
        for i in range(n - 2, -1, -1):
            if now_t - timex[i] >= window:
                old = _f(temp2[i])
                span = now_t - timex[i]
                if old is None or span <= 0:
                    return None
                return round((now_v - old) / span * 60.0, 1)
        return None

    def machine(self) -> dict[str, Any]:
        """Actuator state straight from the Kaleido driver, if one is connected."""
        kaleido = getattr(self._aw, 'kaleido', None)
        if kaleido is None:
            return {'connected': False,
                    'note': 'no Kaleido driver on this ApplicationWindow'}
        out: dict[str, Any] = {'connected': True}
        with suppress(Exception):
            hp, fc = kaleido.getHeaterFan()
            out['heater_pct'], out['fan_pct'] = _f(hp), _f(fc)
        with suppress(Exception):
            rc, ah = kaleido.getDrumAH()
            out['drum_pct'] = _f(rc)
            out['machine_pid_on'] = bool(ah) if _f(ah) is not None else None
        with suppress(Exception):
            ts, at = kaleido.getSVAT()
            out['setpoint'], out['ambient'] = _f(ts), _f(at)
        out['heater_state_note'] = (
            'heater_pct is the last COMMANDED value. This machine reports no HS '
            'channel, so there is no confirmation the burner is actually firing.')
        return out

    def status(self) -> dict[str, Any]:
        """The whole read-only picture. This is the one tool of Phase A."""
        qmc = self._aw.qmc
        n = min(len(qmc.timex), len(qmc.temp1), len(qmc.temp2))
        bt = _f(qmc.temp2[n - 1]) if n else None
        et = _f(qmc.temp1[n - 1]) if n else None
        return {
            'ok': True,
            'unit': qmc.mode,
            'unit_source': "Artisan's qmc.mode -- the machine does not report its unit",
            'sampling': bool(qmc.flagon),
            'recording': bool(qmc.flagstart),
            'elapsed_since_charge_s': self.elapsed(),
            'BT': bt,
            'ET': et,
            'ror_per_min': self.ror(),
            'samples': n,
            'milestones': self.milestones(),
            'machine': self.machine(),
            'read_only': True,
            'server_time': round(time.time(), 1),
        }

    # -- server -------------------------------------------------------------

    def _build(self) -> Any:
        from mcp.server import MCPServer

        server = MCPServer(name='artisan', title='Artisan (read-only)',
                           version='0.1.0', instructions=INSTRUCTIONS)

        @server.tool()
        async def roast_status() -> dict[str, Any]:
            """Live state of the roast in Artisan: temperatures, rate of rise,
            elapsed time, which milestones are marked, and the machine's actuator
            settings. Read-only -- this build cannot change the roaster.
            """
            try:
                return self.status()
            except Exception as e:  # pylint: disable=broad-except
                _log.exception(e)
                return {'ok': False, 'error': f'{type(e).__name__}: {e}'}

        return server

    @staticmethod
    def _run_loop(loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
            for task in asyncio.all_tasks(loop):
                task.cancel()
            for t in [t for t in asyncio.all_tasks(loop) if not (t.done() or t.cancelled())]:
                with suppress(asyncio.CancelledError):
                    loop.run_until_complete(t)
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
        finally:
            loop.close()

    def start(self) -> bool:
        """Start the server. Returns False if it could not be started."""
        if self._running:
            return True
        try:
            self._server = self._build()
        except ImportError as e:
            _log.error('MCP server unavailable (is the mcp package installed?): %s', e)
            return False
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_loop, args=(self._loop,),
                              name='artisan-mcp', daemon=True)
        self._thread.start()

        self._server.settings.host = self._host
        self._server.settings.port = self._port
        asyncio.run_coroutine_threadsafe(self._server.run_streamable_http_async(), self._loop)
        self._running = True
        _log.info('MCP server listening on http://%s:%s/mcp (read-only)', self._host, self._port)
        return True

    def stop(self) -> None:
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        self._running = False
        _log.info('MCP server stopped')

    @property
    def running(self) -> bool:
        return self._running
