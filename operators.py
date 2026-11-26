# SPDX-License-Identifier: GPL-3.0-or-later
"""Navigation operators: open root, open level (push), back (pop)."""

import bpy
from bpy.props import StringProperty

from .pie_data import LEVELS, ROOT_LEVEL, EDIT_LEVEL, menu_idname
from .lists import clear_shortcut_cache


# --------------------------------------------------------------------------
# Navigation state
# --------------------------------------------------------------------------
# ``_stack`` holds the levels the user came through; ``_current`` is the level
# currently shown. Opening a sub-pie pushes ``_current``; going back pops.
_stack = []
_current = ROOT_LEVEL
_anchor_xy = None
_saved_wcol_box = None


def _restore_wcol_box():
    global _saved_wcol_box
    if _saved_wcol_box is None:
        return None
    try:
        ui = bpy.context.preferences.themes[0].user_interface
        inner, outline, roundness = _saved_wcol_box
        ui.wcol_box.inner = inner
        ui.wcol_box.outline = outline
        ui.wcol_box.roundness = roundness
    except Exception:
        pass
    _saved_wcol_box = None
    return None


def _apply_pie_box_theme(context):
    """Temporarily match wcol_box to wcol_pie_menu so the dropdown list has
    the exact same opaque background color as the pie menu."""
    global _saved_wcol_box
    try:
        ui = context.preferences.themes[0].user_interface
        if _saved_wcol_box is None:
            _saved_wcol_box = (
                tuple(ui.wcol_box.inner),
                tuple(ui.wcol_box.outline),
                float(ui.wcol_box.roundness),
            )
        ui.wcol_box.inner = tuple(ui.wcol_pie_menu.inner)
        ui.wcol_box.outline = tuple(ui.wcol_pie_menu.outline)
    except Exception:
        pass


def _show(context, level_id, warp_to_anchor=False):
    global _current
    _current = level_id
    win = context.window
    if warp_to_anchor and win is not None and _anchor_xy is not None:
        try:
            win.cursor_warp(_anchor_xy[0], _anchor_xy[1])
        except Exception:
            pass
    _apply_pie_box_theme(context)
    bpy.ops.wm.call_menu_pie('INVOKE_DEFAULT', name=menu_idname(level_id))


def _prefs(context):
    addon = context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def _is_edit_mode(context):
    if context.mode.startswith('EDIT'):
        return True
    obj = context.active_object or context.object
    return obj is not None and obj.mode == 'EDIT'


# --------------------------------------------------------------------------
# Operators
# --------------------------------------------------------------------------
class MLPIE_OT_open_root(bpy.types.Operator):
    """Open the Pie Menu + menu"""
    bl_idname = "mlpie.open_root"
    bl_label = "Pie Menu +"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.area is not None and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        global _anchor_xy
        _stack.clear()
        clear_shortcut_cache()
        if event is not None:
            _anchor_xy = (event.mouse_x, event.mouse_y)
        level = ROOT_LEVEL
        prefs = _prefs(context)
        context_aware = prefs.context_aware_edit if prefs else True
        if context_aware and _is_edit_mode(context):
            level = EDIT_LEVEL
        _show(context, level, warp_to_anchor=False)
        return {'FINISHED'}

    def execute(self, context):
        return self.invoke(context, None)


class MLPIE_OT_open_level(bpy.types.Operator):
    """Open a sub-level pie"""
    bl_idname = "mlpie.open_level"
    bl_label = "Open Pie Level"
    bl_options = {'INTERNAL'}

    level: StringProperty()
    mode: StringProperty(description="Object mode to switch to first (optional)")
    select_mode: StringProperty(description="Mesh select mode VERT/EDGE/FACE (optional)")

    @classmethod
    def description(cls, context, props):
        return "Open the %s pie" % LEVELS.get(props.level, {}).get("label", props.level)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        if self.level not in LEVELS:
            self.report({'ERROR'}, "Unknown pie level: %s" % self.level)
            return {'CANCELLED'}

        obj = context.active_object
        if self.mode:
            if obj is None:
                self.report({'WARNING'}, "No active object")
                return {'CANCELLED'}
            if obj.mode != self.mode:
                try:
                    bpy.ops.object.mode_set(mode=self.mode)
                except (RuntimeError, TypeError) as ex:
                    self.report({'WARNING'}, str(ex).strip())
                    return {'CANCELLED'}

        if self.select_mode and context.mode == 'EDIT_MESH':
            bpy.ops.mesh.select_mode(type=self.select_mode)

        _stack.append(_current)
        _show(context, self.level, warp_to_anchor=True)
        return {'FINISHED'}


class MLPIE_OT_back(bpy.types.Operator):
    """Go back to a previous pie level"""
    bl_idname = "mlpie.back"
    bl_label = "Pie Back"
    bl_options = {'INTERNAL'}

    level: StringProperty(description="Level to return to")
    mode: StringProperty(description="Object mode to switch to first (optional)")

    @classmethod
    def description(cls, context, props):
        return "Back to the %s pie" % LEVELS.get(props.level, {}).get("label", props.level)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        if self.mode and obj is not None and obj.mode != self.mode:
            try:
                bpy.ops.object.mode_set(mode=self.mode)
            except (RuntimeError, TypeError) as ex:
                self.report({'WARNING'}, str(ex).strip())

        target = self.level or (_stack[-1] if _stack else ROOT_LEVEL)
        # Pop until the target is found; if it was never visited (e.g. pie
        # opened context-aware straight into Edit), just jump to it.
        if target in _stack:
            while _stack and _stack[-1] != target:
                _stack.pop()
            _stack.pop()
        else:
            _stack.clear()
            if target != ROOT_LEVEL:
                _stack.append(ROOT_LEVEL)
        _show(context, target, warp_to_anchor=True)
        return {'FINISHED'}


class MLPIE_OT_popup(bpy.types.Operator):
    """Switch the Properties editor tab, then show a menu or panel popup"""
    bl_idname = "mlpie.popup"
    bl_label = "Pie Popup"
    bl_options = {'INTERNAL'}

    menu: StringProperty()
    panel: StringProperty()
    properties_tab: StringProperty(description="Properties editor tab, e.g. MATERIAL, MODIFIER")

    def execute(self, context):
        if self.properties_tab:
            set_properties_tab(context, self.properties_tab)
        if self.panel:
            bpy.ops.wm.call_panel(name=self.panel, keep_open=True)
        elif self.menu:
            bpy.ops.wm.call_menu(name=self.menu)
        return {'FINISHED'}


def set_properties_tab(context, tab):
    """Switch every Properties editor in the current screen to ``tab``."""
    screen = context.screen
    if screen is None:
        return
    for area in screen.areas:
        if area.type != 'PROPERTIES':
            continue
        for space in area.spaces:
            if space.type == 'PROPERTIES':
                try:
                    space.context = tab
                except TypeError:
                    pass  # tab not available for the active object
                area.tag_redraw()


class MLPIE_OT_enum_menu(bpy.types.Operator):
    """Popup a menu for an operator's enum property"""
    bl_idname = "mlpie.enum_menu"
    bl_label = "Enum Menu"
    bl_options = {'INTERNAL'}

    operator: StringProperty()
    prop: StringProperty()

    def execute(self, context):
        op_id = self.operator
        prop_id = self.prop

        def draw_enum(menu_self, _context):
            menu_self.layout.operator_context = 'INVOKE_REGION_WIN'
            menu_self.layout.operator_enum(op_id, prop_id)

        context.window_manager.popup_menu(draw_enum, title="")
        return {'FINISHED'}


classes = (
    MLPIE_OT_open_root,
    MLPIE_OT_open_level,
    MLPIE_OT_back,
    MLPIE_OT_popup,
    MLPIE_OT_enum_menu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    _restore_wcol_box()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
