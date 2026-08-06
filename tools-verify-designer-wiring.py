"""Final check on the merge: build a real ApplicationWindow and exercise the
designer wiring that a plain launch never touches.

A launch only proves the action gets created. enableEditMenus() and
disableEditMenus() run on state transitions, so the restored setEnabled calls
have to be invoked deliberately.

Uses a private QtSingleApplication id so it does not see the running Artisan and
demote itself to viewer mode. Results go to a file, not stdout: artisanlib.main
dup2's /dev/null onto fds 1 and 2 at import time (main.py:133).

Run with the settings backed up -- constructing ApplicationWindow touches QSettings.
"""
import os
import sys
import warnings

warnings.simplefilter('ignore', DeprecationWarning)
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENPYXL_DEFUSEDXML'] = 'False'
sys.path.insert(0, '/Users/rosettawang/Documents/artisan/src')

RESULTS = '/private/tmp/claude-501/-Users-rosettawang-Documents-artisan/7f012a98-714c-47de-a76b-bfdb5fa5d7f1/scratchpad/verify-results.txt'
PASS, FAIL = [], []
OUT = None


def emit(line):
    OUT.write(line + os.linesep)
    OUT.flush()


def check(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    emit(f'  {"PASS" if cond else "FAIL"}  {name}  {"" if cond else detail}')


import artisanlib.main as amain                                        # noqa: E402
from artisanlib.main import ApplicationWindow, initialize_locale        # noqa: E402

OUT = open(RESULTS, 'w')

try:
    # main.py creates the Artisan() singleton at import (line 564) with fixed
    # GUIDs, so reuse it rather than building a second QApplication.
    app = amain.app
    emit(f'         artisanviewerMode={app.artisanviewerMode} '
         f'(True means the installed Artisan is running; menu checks may be skipped)')

    locale_str = initialize_locale(app)
    aw = ApplicationWindow(locale=locale_str, artisanviewerFirstStart=False)
    check('ApplicationWindow constructs', aw is not None)

    # --- both designer actions exist and are distinct ---------------------
    check('designerAction exists (upstream, in-app)', hasattr(aw, 'designerAction'))
    check('standaloneDesignerAction exists (fork)', hasattr(aw, 'standaloneDesignerAction'))
    a, b = aw.designerAction.text(), aw.standaloneDesignerAction.text()
    check('labels are distinct', a != b, f'{a!r} vs {b!r}')
    emit(f'         in-app={a!r}   standalone={b!r}')

    # --- both are actually in the Tools menu ------------------------------
    menu = getattr(aw, 'ToolkitMenu', None)
    if menu is not None:
        acts = menu.actions()
        check('Tools menu contains the in-app Designer', aw.designerAction in acts)
        check('Tools menu contains the standalone Profile Designer', aw.standaloneDesignerAction in acts)
        emit(f'         Tools menu: {[x.text() for x in acts if x.text()]}')
    else:
        check('ToolkitMenu built', False, 'ToolkitMenu missing')

    # --- the restored enable/disable logic (what a launch never exercises) --
    aw.enableEditMenus()
    check('enableEditMenus() enables designerAction', aw.designerAction.isEnabled())

    aw.disableEditMenus(designer=False)
    check('disableEditMenus(designer=False) disables it', not aw.designerAction.isEnabled())

    aw.disableEditMenus(designer=True)
    check('disableEditMenus(designer=True) leaves it enabled', aw.designerAction.isEnabled())

    aw.enableEditMenus()
    check('enableEditMenus() re-enables after disable', aw.designerAction.isEnabled())

    # --- the fork's launcher ----------------------------------------------
    check('launchStandaloneDesigner is callable', callable(getattr(aw, 'launchStandaloneDesigner', None)))
    from artisanlib.designer import StandaloneDesignerWindow            # noqa: E402
    check('StandaloneDesignerWindow imports', StandaloneDesignerWindow is not None)

except Exception:
    import traceback
    emit('  EXCEPTION:')
    emit(traceback.format_exc())
    FAIL.append('uncaught exception')

emit(f'{os.linesep}{len(PASS)} passed, {len(FAIL)} failed')
for f in FAIL:
    emit('  - ' + f)
OUT.close()

os._exit(1 if FAIL else 0)  # hard exit: skip Qt teardown and any settings write
