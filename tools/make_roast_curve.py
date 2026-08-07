#!/usr/bin/env python3
"""Generate a smooth Artisan background profile for a bay nut roast.

Curves are PARAMETRIC, not resampled from a recording. A curve built by
resampling real data carries the sensor noise with it, and Artisan's delta-BT
trace turns that into a spiky mess that is impossible to read against a live
roast. The model here gives a clean, strictly declining rate of rise.

    RoR(t) declines linearly from R0 to R1 over the roast
    BT(t)  = BT0 + R0*t + (R1 - R0) * t^2 / (2T)

Fix BT0, the target, and the ending RoR; T follows from them:

    T  = 2*(target - BT0) / (R0 + R1)
    R0 = 2*(target - BT0) / T - R1

Fitted against batch #24 (2026-08-06 16:40) with its Air-90% stall removed, the
model lands within ~4F across the whole ramp, and within 0.1F at 24 min.

Usage
    python3 make_roast_curve.py --target 350 --out Designer/nut-roast-350F.alog
    python3 make_roast_curve.py --target 335 --out Designer/nut-roast-335F.alog

Curves generated with the same --charge/--start-ror/--end-ror are SIBLINGS, not
truncations of each other: each one lands on its own target at the ending RoR,
so a 335F curve is slightly steeper early than the 350F curve. That is usually
what you want -- the roast should arrive at the drop temperature at a chosen
rate. Passing --minutes overrides --start-ror rather than shortening a curve.
"""

from __future__ import annotations

import argparse
import ast
import copy
from pathlib import Path

HERE = Path(__file__).resolve().parent
# The template supplies every profile field this script does not compute -- device
# config, event types, roast metadata -- so the output is a profile Artisan will
# load rather than a bare pair of arrays.
#
# Resolved against this file's own directory, then against the original working
# location, so the script runs from either. Overridable with --template. Moved
# into version control Aug 7, 2026: it lived outside any repository, and it is the
# only tool that has ever produced a curve for this machine.
_TEMPLATE_NAME = 'Designer/designer_2025-06-25_0000_nut-roast-338f-corrected-background.alog'
_TEMPLATE_CANDIDATES = (
    HERE / _TEMPLATE_NAME,
    Path.home() / 'Documents/Claude/Projects/roasting' / _TEMPLATE_NAME,
)
TEMPLATE = next((c for c in _TEMPLATE_CANDIDATES if c.exists()), _TEMPLATE_CANDIDATES[0])

# --- defaults learned from batch #24 -----------------------------------------
CHARGE_BT = 190.9   # BT the machine actually settles at on charge
START_ROR = 7.06    # F/min just after charge
END_ROR = 4.50      # F/min at drop -- keep >0 so the curve never flattens out
TAIL_TO = 368.0     # keep climbing past DROP so SV never runs out mid-roast
SAMPLE_DT = 2.0     # seconds between samples
PLAUSIBLE_MAX_ROR = 12.0  # F/min; batch #24 peaked here briefly and never held it


def build_cold(charge_bt: float, target: float, start_ror: float, peak_ror: float,
               peak_at: float, end_ror: float) -> tuple[list[float], list[float], int]:
    """Cold-drum charge: RoR RISES to a peak, then declines.

    A cold charge does not behave like a hot one. On batch #25 (charged at 69.8F)
    RoR climbed from 10.7 to 35.6 F/min over the first six minutes as the drum
    itself came up to temperature, and only then began to fall. A monotonically
    declining curve asks for maximum heat at the one moment the machine can least
    deliver it, so the roast starts behind and never catches up.

        RoR(t) = start -> peak   linearly over [0, peak_at]
                 peak  -> end    linearly over [peak_at, T]

    T follows from the area under that (the total temperature rise).
    """
    span = target - charge_bt
    if span <= 0:
        raise SystemExit(f'target {target} must be above charge temp {charge_bt}')
    rise_area = peak_at * (start_ror + peak_ror) / 2
    if rise_area >= span:
        raise SystemExit(
            f'the ramp-up alone covers {rise_area:.0f}F of the {span:.0f}F needed -- '
            'lower --peak-ror or --peak-at.')
    minutes = peak_at + 2 * (span - rise_area) / (peak_ror + end_ror)

    def bt(t: float) -> float:
        if t <= peak_at:
            return charge_bt + start_ror * t + (peak_ror - start_ror) * t * t / (2 * peak_at)
        u = t - peak_at
        tail = minutes - peak_at
        return (charge_bt + rise_area + peak_ror * u + (end_ror - peak_ror) * u * u / (2 * tail))

    return _sample(bt, minutes, end_ror)


def _sample(bt, minutes: float, end_ror: float) -> tuple[list[float], list[float], int]:
    """Sample a BT(t) function, then tail past DROP and cool."""
    timex: list[float] = []
    temps: list[float] = []
    t = 0.0
    while t <= minutes:
        timex.append(round(t * 60, 1))
        temps.append(round(bt(t), 3))
        t += SAMPLE_DT / 60
    drop = len(timex) - 1
    sec, val = timex[-1], temps[-1]
    while val < TAIL_TO:
        sec += SAMPLE_DT
        val += end_ror * SAMPLE_DT / 60
        timex.append(round(sec, 1))
        temps.append(round(val, 3))
    for _ in range(90):
        sec += SAMPLE_DT
        timex.append(round(sec, 1))
        temps.append(round(max(180.0, temps[-1] - 2.4), 3))
    return timex, temps, drop


def build(charge_bt: float, target: float, start_ror: float, end_ror: float,
          minutes: float | None) -> tuple[list[float], list[float], int]:
    """Return (timex, BT, drop_index)."""
    span = target - charge_bt
    if span <= 0:
        raise SystemExit(f'target {target} must be above charge temp {charge_bt}')
    if minutes is None:
        minutes = 2 * span / (start_ror + end_ror)
    else:
        start_ror = 2 * span / minutes - end_ror
        if start_ror <= end_ror:
            raise SystemExit(
                f'{minutes:g} min to {target:g}F needs a starting RoR of {start_ror:.2f}, '
                f'which is below the ending RoR of {end_ror:.2f} -- RoR would rise through '
                'the roast. Use a shorter time or a lower end RoR.')

    # Batch #24 briefly touched 12 F/min and never sustained it. Anything much
    # above that is a curve the machine cannot follow, and the PID will simply
    # sit at 100% falling further behind.
    if start_ror > PLAUSIBLE_MAX_ROR:
        print(f'WARNING: starting RoR {start_ror:.1f} F/min exceeds anything this machine has '
              f'sustained (~{PLAUSIBLE_MAX_ROR:g} F/min peak on batch #24).\n'
              f'         {minutes:g} min to {target:g}F is likely unreachable; the burner will '
              'peg at 100% and BT will fall behind the curve.')

    def bt(t: float) -> float:
        return charge_bt + start_ror * t + (end_ror - start_ror) * t * t / (2 * minutes)

    return _sample(bt, minutes, end_ror)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--target', type=float, required=True, help='BT at DROP, in F')
    p.add_argument('--out', required=True, help='output .alog path (relative to this folder)')
    p.add_argument('--title', default=None, help="chart title (default 'Nut Roast <target>F (smooth)')")
    p.add_argument('--charge', type=float, default=CHARGE_BT, help=f'BT at charge (default {CHARGE_BT})')
    p.add_argument('--start-ror', type=float, default=START_ROR, help=f'F/min at charge (default {START_ROR})')
    p.add_argument('--end-ror', type=float, default=END_ROR, help=f'F/min at drop (default {END_ROR})')
    p.add_argument('--minutes', type=float, default=None,
                   help='force a roast length; start-ror is then derived instead of used')
    p.add_argument('--peak-ror', type=float, default=None,
                   help='COLD CHARGE: RoR rises to this peak before declining (e.g. 16)')
    p.add_argument('--peak-at', type=float, default=6.0,
                   help='minutes at which RoR peaks on a cold charge (default 6)')
    a = p.parse_args()

    if a.peak_ror is not None:
        timex, temps, drop = build_cold(a.charge, a.target, a.start_ror,
                                        a.peak_ror, a.peak_at, a.end_ror)
    else:
        timex, temps, drop = build(a.charge, a.target, a.start_ror, a.end_ror, a.minutes)
    et = [round(min(v + 28, 395), 3) for v in temps]
    title = a.title or f'Nut Roast {a.target:g}F (smooth)'

    d = copy.deepcopy(ast.literal_eval(TEMPLATE.read_text(encoding='utf-8')))
    d['timex'] = timex
    d['temp2'] = temps
    d['temp1'] = et
    d['timeindex'] = [0, 0, 0, 0, 0, 0, drop, len(timex) - 1]
    d['title'] = title
    d['beans'] = f'Bay nut - dried; parametric curve, DROP {a.target:g}F'
    d['roastingnotes'] = (
        f'Parametric curve: RoR declines linearly to {a.end_ror:g} F/min at DROP. '
        'Keep Air at 50% -- Air 90% stalled batch #24 for 10 minutes. Curve continues past '
        'DROP so SV never stops climbing. The machine cut AH by itself at BT 331F once, so '
        'expect to need MANUAL burner above ~330F. pidOffDROP=True: marking DROP cuts heat at once.')
    d['specialevents'] = [0, drop]
    d['specialeventstype'] = [4, 4]
    d['specialeventsvalue'] = [0, 0]
    d['specialeventsStrings'] = ['CHARGE: Air 50, Drum 40 - do NOT raise Air', f'DROP {a.target:g}F']
    for k in ('alarmflag', 'alarmguard', 'alarmnegguard', 'alarmtime', 'alarmoffset', 'alarmcond',
              'alarmsource', 'alarmtemperature', 'alarmaction', 'alarmbeep', 'alarmstrings'):
        d[k] = []
    d['xmin'], d['xmax'] = -10.0, float(timex[-1] + 30)
    d['ymin'], d['ymax'] = 150, 400

    out = (HERE / a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(repr(d), encoding='utf-8')

    rors = [(temps[i] - temps[i - 30]) / ((timex[i] - timex[i - 30]) / 60) for i in range(30, drop)]
    print(f'wrote {out}')
    print(f'  {title}')
    print(f'  CHARGE {a.charge:g}F -> DROP {temps[drop]:.1f}F at {timex[drop] / 60:.2f} min')
    if a.peak_ror is not None:
        pk = max(range(len(rors)), key=lambda i: rors[i])
        print(f'  RoR {rors[0]:.2f} -> peak {rors[pk]:.2f} at {(timex[pk + 30]) / 60:.1f} min '
              f'-> {rors[-1]:.2f} F/min  (peak mode: rises then eases, by design)')
    else:
        print(f'  RoR {max(rors):.2f} -> {min(rors):.2f} F/min, '
              f'strictly declining: {all(rors[i] >= rors[i + 1] - 1e-9 for i in range(len(rors) - 1))}')
    print(f'  curve continues to {max(temps):.0f}F past DROP')


if __name__ == '__main__':
    main()
