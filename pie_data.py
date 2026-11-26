# SPDX-License-Identifier: GPL-3.0-or-later
"""
Pie layout definitions.

This is the single source of truth for every pie level. It is plain data
(dicts / lists / strings) so it can later be edited from the add-on
preferences or loaded from / saved to JSON.

Level
-----
    "label":    Title drawn at the top of the pie.
    "slots":    Mapping of compass direction -> item. Directions are
                W, E, S, N, NW, NE, SW, SE. Missing directions stay empty.
    "contents": Optional dropdown list drawn in the S (bottom) slot. Either a
                curated list id from ``lists.LISTS`` or a built-in menu
                idname, or a dict mapping ``context.mode`` -> one of those
                (``"*"`` = fallback).

Item ("type" decides the remaining keys)
----------------------------------------
    level     Open another pie.          target, [mode], [select_mode]
    back      Return to a previous pie.  target (pops the stack up to target), [mode]
    menu      Popup a built-in menu.     menu, [properties_tab]
    panel     Popup a panel.             panel, [properties_tab]
    operator  Run an operator.           operator, [props]
    prop      Toggle a property.         data ("tool_settings" | "scene" ...), prop

All items accept "text" and an optional "icon".
"""

ROOT_LEVEL = "MAIN"
EDIT_LEVEL = "EDIT"

LEVELS = {
    # ------------------------------------------------------------------ Main
    "MAIN": {
        "label": "Main",
        "slots": {
            "N":  {"type": "level", "text": "Mode", "target": "MODE"},
            "NW": {"type": "level", "text": "View", "target": "VIEW"},
            "NE": {"type": "level", "text": "Modify", "target": "MODIFY"},
            "W":  {"type": "level", "text": "Edit", "target": "EDIT", "mode": "EDIT"},
            "E":  {"type": "level", "text": "Object", "target": "OBJECT", "mode": "OBJECT"},
            "SW": {"type": "panel", "text": "Material", "panel": "MLPIE_PT_material",
                   "properties_tab": "MATERIAL"},
            "SE": {"type": "level", "text": "Animate", "target": "ANIMATE"},
        },
        "contents": "OBJECT",
    },

    # ------------------------------------------------------------------ Mode
    "MODE": {
        "label": "Mode",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN", "mode": "OBJECT"},
            "NW": {"type": "operator", "text": "Texture Paint", "operator": "object.mode_set",
                   "props": {"mode": "TEXTURE_PAINT"}},
            "NE": {"type": "operator", "text": "Vertex Paint", "operator": "object.mode_set",
                   "props": {"mode": "VERTEX_PAINT"}},
            "W":  {"type": "operator", "text": "Sculpt Mode", "operator": "object.mode_set",
                   "props": {"mode": "SCULPT"}},
            "E":  {"type": "operator", "text": "Weight Paint", "operator": "object.mode_set",
                   "props": {"mode": "WEIGHT_PAINT"}},
            "SW": {"type": "level", "text": "Edit Mode", "target": "EDIT", "mode": "EDIT"},
            "SE": {"type": "operator", "text": "Object Mode", "operator": "object.mode_set",
                   "props": {"mode": "OBJECT"}},
            "S":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
        },
    },

    # ------------------------------------------------------------------ View
    "VIEW": {
        "label": "View",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN"},
            "NW": {"type": "menu", "text": "Cameras", "menu": "VIEW3D_MT_view_cameras"},
            "NE": {"type": "menu", "text": "Navigation", "menu": "VIEW3D_MT_view_navigation"},
            "W":  {"type": "menu", "text": "View Regions", "menu": "VIEW3D_MT_view_regions"},
            "E":  {"type": "menu", "text": "Align View", "menu": "VIEW3D_MT_view_align"},
            "SE": {"type": "menu", "text": "Viewpoint", "menu": "VIEW3D_MT_view_viewpoint"},
        },
        "contents": "VIEW",
    },

    # ---------------------------------------------------------------- Modify
    "MODIFY": {
        "label": "Modify",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN"},
            "NW": {"type": "menu", "text": "Clear", "menu": "VIEW3D_MT_object_clear"},
            "NE": {"type": "menu", "text": "Apply", "menu": "VIEW3D_MT_object_apply"},
            "W":  {"type": "menu", "text": "Mirror", "menu": "VIEW3D_MT_mirror"},
            "E":  {"type": "menu", "text": "Snap", "menu": "VIEW3D_MT_snap"},
            "SW": {"type": "menu", "text": "Set Origin", "menu": "MLPIE_MT_origin_set"},
            "SE": {"type": "prop", "text": "Affect Origin", "data": "tool_settings",
                   "prop": "use_transform_data_origin"},
            "S":  {"type": "menu", "text": "Modifiers", "menu": "OBJECT_MT_modifier_add",
                   "properties_tab": "MODIFIER"},
        },
    },

    # --------------------------------------------------------------- Animate
    "ANIMATE": {
        "label": "Animate",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN"},
            "NW": {"type": "menu", "text": "Constraints", "menu": "VIEW3D_MT_object_constraints"},
            "NE": {"type": "menu", "text": "Parents", "menu": "VIEW3D_MT_object_parent"},
            "W":  {"type": "menu", "text": "In-betweens", "menu": "VIEW3D_MT_pose_slide"},
            "E":  {"type": "menu", "text": "Animate", "menu": "VIEW3D_MT_object_animation"},
            "SW": {"type": "prop", "text": "Auto", "data": "tool_settings",
                   "prop": "use_keyframe_insert_auto"},
            "SE": {"type": "menu", "text": "Transform", "menu": "VIEW3D_MT_transform_object"},
            "S":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
        },
    },

    # ---------------------------------------------------------------- Object
    "OBJECT": {
        "label": "Object",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN"},
            "NW": {"type": "menu", "text": "Convert", "menu": "VIEW3D_MT_object_convert"},
            "NE": {"type": "menu", "text": "Track", "menu": "VIEW3D_MT_object_track"},
            "W":  {"type": "menu", "text": "Rigid Body", "menu": "VIEW3D_MT_object_rigid_body"},
            "E":  {"type": "menu", "text": "Quick Effects", "menu": "VIEW3D_MT_object_quick_effects"},
            "SW": {"type": "menu", "text": "Link/Transfer Data", "menu": "VIEW3D_MT_make_links"},
            "SE": {"type": "menu", "text": "Library Override", "menu": "VIEW3D_MT_object_liboverride"},
            "S":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
        },
    },

    # ------------------------------------------------------------------ Edit
    "EDIT": {
        "label": "Edit",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN", "mode": "OBJECT"},
            "W":  {"type": "level", "text": "Vertex", "target": "VERTEX", "mode": "EDIT",
                   "select_mode": "VERT"},
            "E":  {"type": "level", "text": "Face", "target": "FACE", "mode": "EDIT",
                   "select_mode": "FACE"},
            "SW": {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
            "SE": {"type": "level", "text": "Edge", "target": "EDGE", "mode": "EDIT",
                   "select_mode": "EDGE"},
        },
        "contents": {
            "EDIT_MESH": "EDIT_MESH",
            "EDIT_CURVE": "VIEW3D_MT_edit_curve",
            "EDIT_SURFACE": "VIEW3D_MT_edit_surface",
            "EDIT_ARMATURE": "VIEW3D_MT_edit_armature",
            "EDIT_LATTICE": "VIEW3D_MT_edit_lattice",
            "EDIT_METABALL": "VIEW3D_MT_edit_meta",
            "EDIT_TEXT": "VIEW3D_MT_edit_font",
        },
    },

    # ---------------------------------------------------- Vertex / Edge / Face
    "VERTEX": {
        "label": "Vertex",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN", "mode": "OBJECT"},
            "NW": {"type": "level", "text": "Edge", "target": "EDGE", "mode": "EDIT",
                   "select_mode": "EDGE"},
            "NE": {"type": "level", "text": "Face", "target": "FACE", "mode": "EDIT",
                   "select_mode": "FACE"},
            "W":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
            "E":  {"type": "back", "text": "Edit", "target": "EDIT"},
        },
        "contents": {"EDIT_MESH": "VERTEX"},
    },
    "EDGE": {
        "label": "Edge",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN", "mode": "OBJECT"},
            "NW": {"type": "level", "text": "Vertex", "target": "VERTEX", "mode": "EDIT",
                   "select_mode": "VERT"},
            "NE": {"type": "level", "text": "Face", "target": "FACE", "mode": "EDIT",
                   "select_mode": "FACE"},
            "W":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
            "E":  {"type": "back", "text": "Edit", "target": "EDIT"},
        },
        "contents": {"EDIT_MESH": "EDGE"},
    },
    "FACE": {
        "label": "Face",
        "slots": {
            "N":  {"type": "back", "text": "Main", "target": "MAIN", "mode": "OBJECT"},
            "NW": {"type": "level", "text": "Vertex", "target": "VERTEX", "mode": "EDIT",
                   "select_mode": "VERT"},
            "NE": {"type": "level", "text": "Edge", "target": "EDGE", "mode": "EDIT",
                   "select_mode": "EDGE"},
            "W":  {"type": "menu", "text": "Select", "menu": "MLPIE_MT_select"},
            "E":  {"type": "back", "text": "Edit", "target": "EDIT"},
        },
        "contents": {"EDIT_MESH": "FACE"},
    },
}

# Blender's fixed pie slot order: each call to pie.<item>() fills the next one.
PIE_ORDER = ("W", "E", "S", "N", "NW", "NE", "SW", "SE")


def menu_idname(level_id):
    """Class idname of the generated pie menu for a level."""
    return "MLPIE_MT_pie_" + level_id.lower()
