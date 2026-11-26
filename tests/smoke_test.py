# SPDX-License-Identifier: GPL-3.0-or-later
"""
Smoke test. Run with:
    blender --background --factory-startup --python tests/smoke_test.py
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import multilevel_pie  # noqa: E402
from multilevel_pie.pie_data import LEVELS, menu_idname  # noqa: E402
from multilevel_pie.lists import LISTS  # noqa: E402

errors = []
multilevel_pie.register()

valid_icons = {
    i.identifier for i in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
}

for level_id, level in LEVELS.items():
    if not hasattr(bpy.types, menu_idname(level_id)):
        errors.append("pie not registered: " + level_id)
    contents = level.get("contents")
    names = [contents] if isinstance(contents, str) else list((contents or {}).values())
    for name in names:
        if name not in LISTS and not hasattr(bpy.types, name):
            errors.append("%s: missing contents menu %s" % (level_id, name))
    for direction, item in level["slots"].items():
        where = "%s.%s" % (level_id, direction)
        if item.get("icon") and item["icon"] not in valid_icons:
            errors.append("%s: invalid icon %s" % (where, item["icon"]))
        t = item["type"]
        if t in {"level", "back"} and item["target"] not in LEVELS:
            errors.append("%s: unknown target %s" % (where, item["target"]))
        if t == "menu" and not hasattr(bpy.types, item["menu"]):
            errors.append("%s: missing menu %s" % (where, item["menu"]))
        if t == "panel" and not hasattr(bpy.types, item["panel"]):
            errors.append("%s: missing panel %s" % (where, item["panel"]))
        if t == "prop" and item["data"] == "tool_settings":
            if item["prop"] not in bpy.types.ToolSettings.bl_rna.properties:
                errors.append("%s: missing property %s" % (where, item["prop"]))

for op in ("open_root", "open_level", "back"):
    if not hasattr(bpy.types, "MLPIE_OT_" + op):
        errors.append("operator not registered: " + op)

multilevel_pie.unregister()

print("Blender", bpy.app.version_string)
if errors:
    print("SMOKE TEST FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("SMOKE TEST PASSED")
