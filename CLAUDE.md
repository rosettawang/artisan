# Artisan fork — working notes

A fork of [artisan-roaster-scope/artisan](https://github.com/artisan-roaster-scope/artisan) for one roastery: an MCP control surface, and adaptations for a Kaleido roaster. Upstream is alive and moves fast — 433 commits landed between Nov 2025 and Aug 2026 — so everything here is written to keep rebasing cheap.

## Branches

- `main` — **the default branch and the only one that matters.** Carries the 2025 fork work (standalone Profile Designer, Kaleido BT-only mode, curve smoothness, cap-burner-output), merged forward onto 4.2.1 on Aug 6, 2026 (`738dcd16c`), plus `specs/`.
- `master` — **deleted** Aug 6, 2026, locally and on the remote. It only ever mirrored upstream, and `upstream/master` already does that. For a pristine upstream reference use `git fetch upstream && git log upstream/master`.
- `mcp-kaleido-adaptations` — local-only, points at the same commit as `main`. Redundant; delete when convenient.

Pull upstream *before* starting a phase, not after. Every source file a spec touches is a future conflict, which is why specs declare `spec-touches` and prefer new files to edits.

## Specs

- **Specs live in `specs/`, one file per unbuilt feature — as `.html`, not `.md`** (owner preference: specs are read rendered in a browser). A spec's lifecycle is **declared, not remembered**: each carries `<meta name="spec-status" content="open|blocked|done|canonical">`, and `./specs.sh prune` deletes the `done` ones, logs a dated completion note, and strikes them everywhere. Set the status and run the prune in the shipping commit. Git history is the archive — **never "update" a shipped spec**.
- **Writing a new spec:** copy the `<head>` from any existing file in `specs/`, link the shared stylesheet (`<link rel="stylesheet" href="spec.css">`), write semantic HTML, and give it a `<p class="lede">` — the prune uses it as the one-line summary. Declare at minimum `spec-status`; add `spec-touches` (files it edits, for conflict detection and ordering), `spec-needs` (slugs that must land first), `spec-blocker` (one dated line of what remains), `spec-decision` (one per owner choice), and `spec-verify` (a shell command that exits 0 when done). The full table is in the folded **Reference** at the bottom of `specs/index.html`.
- **`specs/index.html` is the dashboard, and mostly generated.** `./specs.sh prune` rewrites the **Live specs** list, **Decisions waiting**, **Recently completed**, the **spec-pass** block, and (chained via `plan --write`) the **Execution order** — all between `GENERATED:*` markers. **Never hand-edit inside those markers.** Three sections *are* hand-maintained: the **Hardware pass**, the **Bottlenecks**, and the **Reconciliations**.
- **Every spec run ends with its outcome recorded.** (1) A step needs the owner at the roaster → a **Hardware pass** row; (2) a choice only the owner can make → a `spec-decision` meta, with the recommended answer and whether it blocks — never silently pick and bury it in a commit; (3) built behaviour deviates from the spec text → a **Reconciliations** row *and* an edit to the owning spec so it reads true. Then `./specs.sh prune`. Multi-spec runs append to `specs/RUN-LOG.html` as they go.
- Don't create new top-level `.md` files. New design → an `.html` file in `specs/`.

## How specs get worked

<!-- SPEC-PASS:START -->
**Spec pass — how specs get worked, by default.** No further prompting should be needed: the session runs the whole thing without asking what to do next.

1. **Reassess the spec first.** A spec is a starting point, not a contract. Check its claims against the current code and the machine before building — specs here go stale, and this one's neighbours went stale inside a single session. Where reality has moved, correct the spec and say what changed.
2. **Sequence it, then work the sequence end to end.** Don't stop after one item to report progress, and don't ask which item to do next.
3. **Use discretion to build it out.** Fill gaps the spec left, fix what it got wrong, improve on it where the better design is clear. Note the deviations.
4. **Stop only at a blocker or a decision** — a step needing the owner at the roaster, anything that puts heat into a drum, or a choice that is structural and hard to reverse. Not on mere uncertainty: if a call is cheap and reversible, make it, note it, keep going. "Stop" means stop that spec, never the session.
5. **Log the stop** in that spec's `spec-blocker` meta, then run `./specs.sh prune` so the index reflects it.
6. **Declare each decision separately**, one `spec-decision` meta per choice, stating the recommended answer and whether it blocks. Burying a decision in blocker prose leaves it unfindable.

Verify as you go rather than at the end — but be honest about what verification is available here. The suite needs Python 3.12+, and no test in this repo can tell you whether a burner command did what you expected. That answer only comes from standing at the machine.
<!-- SPEC-PASS:END -->

## Spec tooling — `./specs.sh`

Stdlib-only Node in `scripts/*.mjs` behind one entry point. `check` = dry run, writes nothing. `prune` = delete `done` specs, regenerate the index, redraw the order (**one command**; never run `plan` separately after pruning, that leaves the order linking to a deleted file). `plan` = print the order without pruning.

**No `package.json`, deliberately** — this is a Python app, and a root Node manifest would mislabel the repo for every tool that sniffs one.

## The roaster is real

This fork can command a burner on a machine holding hot coffee. Non-negotiable:

- **Writes are refused until armed**, in a time-boxed window. Reads are never gated.
- **Limits are enforced below the tool layer**, so no prompt can talk past them: heater ceiling, max step, airflow interlock, BT/ET ceilings.
- **Never drive a roast the owner is not watching.** No unattended heat, ever.
- **Software acknowledgement is not observation.** This machine reports no `HS`, so "the heater is off" means *a command was acknowledged*. Say so wherever it is surfaced, including in `emergency_stop`.
- **No write has ever been sent to the physical roaster.** Until that changes, every actuator behaviour in this repo is inference from `artisanlib/kaleido.py`.

## Verifying

Artisan 4.2.x needs **Python 3.12+** — `src/pyproject.toml` declares `requires-python = '>=3.12'` (raised upstream in `6908b688c`, Nov 2025); CI runs 3.14. The repo's `venv/` is 3.9 and cannot run it — do not read a passing command in that venv as a passing test.

**Isolate the preferences domain before running the suite.** `test/unitary/artisanlib/test_main.py` constructs a bare `QSettings()` and writes to it — verified Aug 6, 2026, when a plain `pytest test/` put `SomeOtherSetting=keep_this` and `test_group.test_key` into the owner's live `org.artisan-scope.Artisan.plist`, reset `starts` to 0, and deleted every window-geometry key (`Geometry`, `MainWindowState`, `PIDPosition`, `PortsGeometry`, `RoastGeometry`, `BackgroundGeometry`, `DeviceAssignmentGeometry`). Device and roasting settings survived, but that was luck, not design. Back up the plist first, and prefer running with an isolated `HOME`:

```
cp ~/Library/Preferences/org.artisan-scope.Artisan.plist /tmp/artisan-settings-backup.plist
HOME=$(mktemp -d) .venv313/bin/python -m pytest test/ -q
```

A parse check is not a test. `python -c "import ast; ast.parse(...)"` on a 3.11 interpreter **fails on untouched upstream files**, because they use PEP 695 `type X = ...` syntax — verified against `canvas.py` on Aug 6, 2026. Check against 3.12+ or don't claim it.
