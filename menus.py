# SPDX-License-Identifier: GPL-3.0-or-later
"""Pie menu classes generated from ``pie_data`` plus helper menus/panels."""

import bpy

from .pie_data import LEVELS, PIE_ORDER, menu_idname
from .lists import draw_list

_VALID_ICONS = set()


def _icon(name):
    """Return a valid icon name, falling back to NONE (icons change between versions)."""
    if not _VALID_ICONS:
        _VALID_ICONS.update(
            i.identifier for i in bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
        )
    return name if name in _VALID_ICONS else 'NONE'


def _resolve_contents(spec, context):
    """``contents`` may be a menu idname or a dict keyed by context.mode."""
    if not spec:
        return None
    if isinstance(spec, str):
        return spec
    return spec.get(context.mode) or spec.get("*")


# --------------------------------------------------------------------------
# Item drawing
# --------------------------------------------------------------------------
def draw_item(layout, context, item, pad_text=False):
    kind = item.get("type")
    text = item.get("text", "")
    icon = _icon(item.get("icon", 'NONE'))
    if pad_text and icon == 'NONE':
        text = "      " + text

    if kind == "level":
        op = layout.operator("mlpie.open_level", text=text, icon=icon)
        op.level = item["target"]
        op.mode = item.get("mode", "")
        op.select_mode = item.get("select_mode", "")

    elif kind == "back":
        op = layout.operator("mlpie.back", text=text, icon=icon)
        op.level = item.get("target", "")
        op.mode = item.get("mode", "")

    elif kind == "menu":
        menu = item["menu"]
        if not hasattr(bpy.types, menu):
            layout.label(text=text + " (missing)", icon='ERROR')
        elif item.get("properties_tab"):
            op = layout.operator("mlpie.popup", text=text, icon=icon)
            op.menu = menu
            op.properties_tab = item["properties_tab"]
        else:
            layout.operator("wm.call_menu", text=text, icon=icon).name = menu

    elif kind == "panel":
        op = layout.operator("mlpie.popup", text=text, icon=icon)
        op.panel = item["panel"]
        op.properties_tab = item.get("properties_tab", "")

    elif kind == "operator":
        op = layout.operator(item["operator"], text=text, icon=icon)
        for key, value in item.get("props", {}).items():
            setattr(op, key, value)

    elif kind == "prop":
        data = getattr(context, item["data"], None)
        if data is not None:
            active = bool(getattr(data, item["prop"], False))
            op = layout.operator("wm.context_toggle", text=text, icon=icon, depress=active)
            op.data_path = "%s.%s" % (item["data"], item["prop"])
        else:
            layout.separator()

    else:
        layout.separator()


# --------------------------------------------------------------------------
# Generated pie menus
# --------------------------------------------------------------------------
def _show_trigger_numbers(context):
    addon = context.preferences.addons.get(__package__)
    if addon and addon.preferences:
        return addon.preferences.show_trigger_numbers
    return False


def _draw_pie_slot(pie, context, item, show_numbers):
    """Draw a single pie slot. Wrapping the button in a sub-row with PIE_MENU
    emboss suppresses Blender's automatic 1-9 numpad shortcut label while
    keeping the full dark Pie Menu button size and centering the text."""
    if show_numbers:
        draw_item(pie, context, item, pad_text=False)
    else:
        sub = pie.row(align=True)
        sub.emboss = 'PIE_MENU'
        sub.scale_y = 1.5
        draw_item(sub, context, item, pad_text=True)


def _make_pie_class(level_id, level):
    def draw(self, context):
        pie = self.layout.menu_pie()
        slots = level.get("slots", {})
        contents = _resolve_contents(level.get("contents"), context)
        show_numbers = _show_trigger_numbers(context)

        for direction in PIE_ORDER:
            item = slots.get(direction)
            if direction == "S" and contents:
                col = pie.column()
                if item:
                    _draw_pie_slot(col, context, item, show_numbers)
                draw_list(col, context, contents)
            elif item:
                _draw_pie_slot(pie, context, item, show_numbers)
            else:
                pie.separator()

        # Invisible spacer on the root layout so the pie block's logical bounds
        # exceed the window size; this prevents Blender from shifting the pie
        # center away from the cursor when triggered near editor/window edges
        # or when the S dropdown list overflows.
        bounds = self.layout.column()
        bounds.ui_units_x = 500
        bounds.separator(factor=500)

    return type(
        menu_idname(level_id),
        (bpy.types.Menu,),
        {
            "bl_idname": menu_idname(level_id),
            "bl_label": level.get("label", level_id),
            "draw": draw,
        },
    )


# --------------------------------------------------------------------------
# Helper popups
# --------------------------------------------------------------------------
class MLPIE_MT_origin_set(bpy.types.Menu):
    bl_idname = "MLPIE_MT_origin_set"
    bl_label = "Set Origin"

    def draw(self, context):
        self.layout.operator_enum("object.origin_set", "type")


class MLPIE_MT_select(bpy.types.Menu):
    """Context-aware Select menu matching the 3D Viewport header Select menu."""
    bl_idname = "MLPIE_MT_select"
    bl_label = "Select"

    def draw(self, context):
        mode = context.mode
        obj = context.active_object
        menu_name = "VIEW3D_MT_select_" + mode.lower()
        if mode in {'PAINT_WEIGHT', 'PAINT_VERTEX', 'PAINT_TEXTURE'} and obj and obj.type == 'MESH':
            if obj.data.use_paint_mask_vertex and mode in {'PAINT_WEIGHT', 'PAINT_VERTEX'}:
                menu_name = "VIEW3D_MT_select_paint_mask_vertex"
            else:
                menu_name = "VIEW3D_MT_select_paint_mask"
        elif mode == 'SCULPT_CURVES':
            menu_name = "VIEW3D_MT_select_sculpt_curves"
        elif mode in {
            'VERTEX_GREASE_PENCIL',
            'PAINT_GREASE_PENCIL',
            'SCULPT_GREASE_PENCIL',
            'WEIGHT_GREASE_PENCIL',
        }:
            menu_name = "VIEW3D_MT_select_edit_grease_pencil"
        if not hasattr(bpy.types, menu_name):
            menu_name = "VIEW3D_MT_select_object"
        self.layout.menu_contents(menu_name)


class MLPIE_PT_material(bpy.types.Panel):
    """Material slot popup (pick material, assign, add/remove slots)."""
    bl_idname = "MLPIE_PT_material"
    bl_label = "Material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'HEADER'
    bl_ui_units_x = 14

    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        if ob is None or not hasattr(ob, "material_slots"):
            layout.label(text="No active object with materials", icon='INFO')
            return

        layout.label(text=ob.name, icon='MATERIAL')
        row = layout.row()
        row.template_list(
            "MATERIAL_UL_matslots", "mlpie", ob, "material_slots",
            ob, "active_material_index", rows=4,
        )
        col = row.column(align=True)
        col.operator("object.material_slot_add", icon='ADD', text="")
        col.operator("object.material_slot_remove", icon='REMOVE', text="")
        col.separator()
        col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        layout.template_ID(ob, "active_material", new="material.new")

        if ob.mode == 'EDIT':
            row = layout.row(align=True)
            row.operator("object.material_slot_assign", text="Assign")
            row.operator("object.material_slot_select", text="Select")
            row.operator("object.material_slot_deselect", text="Deselect")


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------
_pie_classes = []
_static_classes = (MLPIE_MT_origin_set, MLPIE_MT_select, MLPIE_PT_material)


def register():
    for cls in _static_classes:
        bpy.utils.register_class(cls)
    _pie_classes.clear()
    for level_id, level in LEVELS.items():
        cls = _make_pie_class(level_id, level)
        bpy.utils.register_class(cls)
        _pie_classes.append(cls)


def unregister():
    for cls in reversed(_pie_classes):
        bpy.utils.unregister_class(cls)
    _pie_classes.clear()
    for cls in reversed(_static_classes):
        bpy.utils.unregister_class(cls)
