# SPDX-License-Identifier: GPL-3.0-or-later
"""
Trigger key registration (default: Right Mouse in the 3D Viewport).

Blender's own RMB context menus live in the per-mode keymaps ("Object Mode",
"Mesh", "Pose", "Sculpt", ...). Those are evaluated *before* the generic
"3D View" keymap, so the trigger must be added to every mode keymap or the
context menu swallows the event. The operator polls for a 3D Viewport, so if
it doesn't apply the event falls through to Blender's default behaviour.
"""

import bpy

TRIGGER_OPERATOR = "mlpie.open_root"

# (keymap name, space_type) - names from Blender's default keymap.
KEYMAPS = (
    ("Object Mode", 'EMPTY'),
    ("Mesh", 'EMPTY'),
    ("Curve", 'EMPTY'),
    ("Curves", 'EMPTY'),
    ("Armature", 'EMPTY'),
    ("Metaball", 'EMPTY'),
    ("Lattice", 'EMPTY'),
    ("Font", 'EMPTY'),
    ("Pose", 'EMPTY'),
    ("Particle", 'EMPTY'),
    ("Sculpt", 'EMPTY'),
    ("Vertex Paint", 'EMPTY'),
    ("Weight Paint", 'EMPTY'),
    ("Image Paint", 'EMPTY'),
    ("Grease Pencil Edit Mode", 'EMPTY'),
    ("Grease Pencil Draw Mode", 'EMPTY'),
    ("Grease Pencil Sculpt Mode", 'EMPTY'),
    ("Grease Pencil Weight Paint", 'EMPTY'),
    ("Grease Pencil Vertex Paint", 'EMPTY'),
    ("3D View", 'VIEW_3D'),
)

_addon_keymaps = []


def _trigger_settings():
    """Read trigger settings from the add-on preferences (with defaults)."""
    settings = {"type": 'RIGHTMOUSE', "shift": False, "ctrl": False, "alt": False, "oskey": False}
    addon = bpy.context.preferences.addons.get(__package__)
    if addon is not None and addon.preferences is not None:
        p = addon.preferences
        settings.update(type=p.trigger_key, shift=p.trigger_shift, ctrl=p.trigger_ctrl,
                        alt=p.trigger_alt, oskey=p.trigger_oskey)
    return settings


def register():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:  # background mode
        return
    s = _trigger_settings()
    for name, space in KEYMAPS:
        km = kc.keymaps.new(name=name, space_type=space)
        kmi = km.keymap_items.new(
            TRIGGER_OPERATOR, s["type"], 'PRESS',
            shift=s["shift"], ctrl=s["ctrl"], alt=s["alt"], oskey=s["oskey"],
        )
        _addon_keymaps.append((km, kmi))


def unregister():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    _addon_keymaps.clear()


def refresh():
    """Re-create keymap items after the trigger settings change."""
    unregister()
    register()
