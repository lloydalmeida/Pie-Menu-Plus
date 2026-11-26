# SPDX-License-Identifier: GPL-3.0-or-later
"""Add-on preferences: trigger key binding and behaviour options."""

import bpy
from bpy.props import BoolProperty, EnumProperty

from . import keymaps

_EVENT_TYPES = [
    (i.identifier, i.name, i.description)
    for i in bpy.types.Event.bl_rna.properties["type"].enum_items
    if i.identifier not in {'NONE'}
]


def _update_trigger(self, context):
    keymaps.refresh()


class MLPIE_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    trigger_key: EnumProperty(
        name="Key",
        description="Key, mouse or pen button that opens the pie menu",
        items=_EVENT_TYPES,
        default='RIGHTMOUSE',
        update=_update_trigger,
    )
    trigger_shift: BoolProperty(name="Shift", update=_update_trigger)
    trigger_ctrl: BoolProperty(name="Ctrl", update=_update_trigger)
    trigger_alt: BoolProperty(name="Alt", update=_update_trigger)
    trigger_oskey: BoolProperty(name="OS Key", update=_update_trigger)

    context_aware_edit: BoolProperty(
        name="Context-Aware Edit Mode",
        description="When triggered in Edit Mode, open the Edit pie directly instead of Main",
        default=True,
    )

    show_trigger_numbers: BoolProperty(
        name="Show Trigger Numbers",
        description="Show numeric shortcut numbers (1-9) on pie menu items",
        default=False,
    )

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Trigger (3D Viewport)", icon='MOUSE_RMB')
        row = box.row(align=True)
        row.prop(self, "trigger_key", text="")
        row.prop(self, "trigger_shift", toggle=True)
        row.prop(self, "trigger_ctrl", toggle=True)
        row.prop(self, "trigger_alt", toggle=True)
        row.prop(self, "trigger_oskey", toggle=True)
        box.label(text="Overrides Blender's context menu for this key in all 3D Viewport modes.", icon='INFO')

        box = layout.box()
        box.label(text="Behaviour", icon='PREFERENCES')
        box.prop(self, "context_aware_edit")
        box.prop(self, "show_trigger_numbers")

        box = layout.box()
        box.label(text="Pie Layout", icon='MENU_PANEL')
        box.label(text="Menu editor coming soon. Layouts are defined in pie_data.py for now.")


def register():
    bpy.utils.register_class(MLPIE_AddonPreferences)


def unregister():
    bpy.utils.unregister_class(MLPIE_AddonPreferences)
