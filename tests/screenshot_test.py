# SPDX-License-Identifier: GPL-3.0-or-later
"""
Visual check: opens one pie level in a real Blender window and saves a screenshot.

    blender --factory-startup --python tests/screenshot_test.py -- LEVEL OUT.png

LEVEL is a key of pie_data.LEVELS (MAIN, VIEW, EDIT, VERTEX, ...).
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import multilevel_pie  # noqa: E402
from multilevel_pie import operators  # noqa: E402
from multilevel_pie.pie_data import menu_idname  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
LEVEL = argv[0] if argv else "MAIN"
OUT = os.path.abspath(argv[1] if len(argv) > 1 else "/tmp/mlpie_%s.png" % LEVEL.lower())
Y_FRAC = float(argv[2]) if len(argv) > 2 else 0.65

multilevel_pie.register()


def _view3d():
    win = bpy.context.window_manager.windows[0]
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            region = next(r for r in area.regions if r.type == 'WINDOW')
            return win, area, region
    raise RuntimeError("no 3D view")


def open_pie():
    win, area, region = _view3d()
    with bpy.context.temp_override(window=win, area=area, region=region):
        if LEVEL in {"EDIT", "VERTEX", "EDGE", "FACE"}:
            bpy.ops.object.mode_set(mode='EDIT')
        win.cursor_warp(region.x + region.width // 2, region.y + int(region.height * Y_FRAC))
        operators._current = LEVEL
        operators._apply_pie_box_theme(bpy.context)
        bpy.ops.wm.call_menu_pie('INVOKE_DEFAULT', name=menu_idname(LEVEL))
    bpy.app.timers.register(shot, first_interval=1.5)
    return None


def shot():
    win, area, region = _view3d()
    with bpy.context.temp_override(window=win, area=area, region=region):
        bpy.ops.screen.screenshot(filepath=OUT)
    print("SCREENSHOT", OUT)
    bpy.app.timers.register(lambda: os._exit(0), first_interval=0.3)
    return None


bpy.app.timers.register(open_pie, first_interval=2.0)
