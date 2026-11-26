# SPDX-License-Identifier: GPL-3.0-or-later
"""
Curated dropdown lists shown under the pies.

Each list contains *exactly* the entries from the reference design (a trimmed
copy of Blender 5.2's built-in menus; entries that live on pie slots instead
are left out).

Lists are drawn to look like Blender's pulldown menus: menu-style buttons on a
dark menu background, without icons or keyboard shortcuts.
"""

import bpy

# Fraction of a list row used by the button when a submenu arrow is shown.
SUBMENU_SPLIT = 0.90


def clear_shortcut_cache():
    pass


class MenuList:
    """Small layout wrapper that draws menu-style rows without icons or shortcuts."""

    def __init__(self, layout, context):
        self.col = layout
        self.context = context

    @property
    def operator_context(self):
        return self.col.operator_context

    @operator_context.setter
    def operator_context(self, value):
        self.col.operator_context = value

    def _row(self, submenu=False):
        """Return the layout for the button. When there is a submenu arrow,
        split the row and draw the arrow right-aligned."""
        if not submenu:
            return self.col.row(align=True)
        split = self.col.split(factor=SUBMENU_SPLIT, align=True)
        left = split.row(align=True)
        right = split.row(align=True)
        right.active = False
        right.alignment = 'RIGHT'
        right.label(text="", icon='TRIA_RIGHT')
        return left

    def op(self, idname, text=None, icon='NONE', **props):
        row = self._row(submenu=False)
        kw = {"icon": 'NONE'}
        if text is not None:
            kw["text"] = text
        ptr = row.operator(idname, **kw)
        for k, v in props.items():
            target = ptr
            parts = k.split(".")
            for p in parts[:-1]:
                target = getattr(target, p)
            setattr(target, parts[-1], v)

    def menu(self, name, text=None, icon='NONE'):
        row = self._row(submenu=True)
        kw = {"icon": 'NONE'}
        if text is not None:
            kw["text"] = text
        row.menu(name, **kw)

    def enum_menu(self, idname, prop, text=None):
        op = self._row(submenu=True).operator("mlpie.enum_menu", text=text or "", icon='NONE')
        op.operator = idname
        op.prop = prop

    def prop(self, data, prop, text=None):
        row = self._row(submenu=False)
        if text is not None:
            row.prop(data, prop, text=text)
        else:
            row.prop(data, prop)

    def sep(self):
        self.col.separator()


# --------------------------------------------------------------------------
# Lists
# --------------------------------------------------------------------------
def _object(m, context):
    ob = context.object
    m.op("object.duplicate_move")
    m.op("object.duplicate_move_linked")
    m.op("object.join")
    m.sep()
    m.op("view3d.copybuffer", text="Copy Objects")
    m.op("view3d.pastebuffer", text="Paste Objects")
    m.sep()
    m.menu("VIEW3D_MT_object_asset")
    m.menu("VIEW3D_MT_object_collection")
    m.sep()
    m.op("object.shade_smooth")
    if ob and ob.type in {'MESH', 'CURVE', 'FONT'}:
        m.op("object.shade_auto_smooth")
    m.op("object.shade_flat")
    m.sep()
    m.menu("VIEW3D_MT_object_showhide")
    m.menu("VIEW3D_MT_object_cleanup")
    m.sep()
    m.operator_context = 'EXEC_REGION_WIN'
    m.op("object.delete", text="Delete", use_global=False)
    m.op("object.delete", text="Delete Global", use_global=True)


def _view(m, context):
    view = context.space_data
    m.prop(view, "show_region_tool_header")
    m.prop(view, "show_region_asset_shelf")
    m.prop(view, "show_region_hud")
    m.sep()
    if context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT', 'SCULPT'}:
        m.op("view3d.view_selected", text="Center Last Stroke")
    else:
        m.op("view3d.view_selected", text="Frame Selected")
    m.op("view3d.view_all", center=False)
    m.op("view3d.view_persportho", text="Perspective/Orthographic")
    m.menu("VIEW3D_MT_view_local")
    m.prop(view, "show_viewer", text="Viewer Node")
    m.sep()
    m.op("screen.animation_play", text="Play Animation")
    m.sep()
    m.op("render.opengl", text="Render Viewport Preview", icon='RENDER_STILL')
    m.op("render.opengl", text="Render Playblast", icon='RENDER_ANIMATION', animation=True)
    m.op("render.opengl", text="Render Playblast on Keyframes", icon='RENDER_ANIMATION',
         animation=True, render_keyed_only=True)
    m.sep()
    m.menu("INFO_MT_area")


def _edit_mesh(m, context):
    m.op("mesh.duplicate_move", text="Duplicate")
    m.menu("VIEW3D_MT_edit_mesh_extrude")
    m.sep()
    m.menu("VIEW3D_MT_edit_mesh_merge", text="Merge")
    m.menu("VIEW3D_MT_edit_mesh_split", text="Split")
    m.enum_menu("mesh.separate", "type", text="Separate")
    m.sep()
    m.op("mesh.bisect")
    m.op("mesh.knife_project")
    m.op("mesh.knife_tool", use_occlude_geometry=True, only_selected=False)
    if bpy.app.build_options.bullet:
        m.op("mesh.convex_hull")
    m.sep()
    m.op("mesh.symmetrize")
    m.op("mesh.symmetry_snap")
    m.sep()
    m.menu("VIEW3D_MT_edit_mesh_normals")
    m.menu("VIEW3D_MT_edit_mesh_shading")
    m.menu("VIEW3D_MT_edit_mesh_weights")
    m.op("mesh.attribute_set")
    m.enum_menu("mesh.sort_elements", "type", text="Sort Elements")
    m.sep()
    m.menu("VIEW3D_MT_edit_mesh_showhide")
    m.menu("VIEW3D_MT_edit_mesh_clean")
    m.sep()
    m.menu("VIEW3D_MT_edit_mesh_delete")


def _vertex(m, context):
    m.op("mesh.extrude_vertices_move", text="Extrude Vertices")
    m.op("mesh.dupli_extrude_cursor", rotate_source=True)
    m.op("mesh.bevel", text="Bevel Vertices", affect='VERTICES')
    m.sep()
    m.op("mesh.edge_face_add", text="New Edge/Face from Vertices")
    m.op("mesh.vert_connect_path", text="Connect Vertex Path")
    m.op("mesh.vert_connect", text="Connect Vertex Pairs")
    m.sep()
    m.op("mesh.rip_move", text="Rip Vertices", **{"MESH_OT_rip.use_fill": False})
    m.op("mesh.rip_move", text="Rip Vertices and Fill", **{"MESH_OT_rip.use_fill": True})
    m.op("mesh.rip_edge_move", text="Rip Vertices and Extend")
    m.sep()
    m.op("transform.vert_slide", text="Slide Vertices")
    m.operator_context = 'EXEC_REGION_WIN'
    m.op("mesh.vertices_smooth", text="Smooth Vertices", factor=0.5)
    m.op("mesh.vertices_smooth_laplacian", text="Smooth Vertices (Laplacian)")
    m.operator_context = 'INVOKE_REGION_WIN'
    m.sep()
    m.op("transform.vert_crease")
    m.sep()
    m.op("mesh.blend_from_shape")
    m.op("mesh.shape_propagate_to_all", text="Propagate to Shapes")
    m.sep()
    m.menu("VIEW3D_MT_vertex_group")
    m.menu("VIEW3D_MT_hook")
    m.sep()
    m.op("object.vertex_parent_set")


def _edge(m, context):
    m.op("mesh.extrude_edges_move", text="Extrude Edges")
    m.op("mesh.bevel", text="Bevel Edges", affect='EDGES')
    m.op("mesh.bridge_edge_loops")
    m.op("mesh.screw")
    m.sep()
    m.op("mesh.subdivide")
    m.op("mesh.subdivide_edgering")
    m.op("mesh.unsubdivide")
    m.sep()
    m.op("mesh.edge_rotate", text="Rotate Edge CW", use_ccw=False)
    m.op("mesh.edge_rotate", text="Rotate Edge CCW", use_ccw=True)
    m.sep()
    m.op("transform.edge_slide")
    m.op("mesh.loopcut_slide", **{"TRANSFORM_OT_edge_slide.release_confirm": False})
    m.op("mesh.offset_edge_loops_slide")
    m.sep()
    m.op("transform.edge_bevelweight")
    m.op("transform.edge_crease")
    m.sep()
    m.op("mesh.mark_seam", clear=False)
    m.op("mesh.mark_seam", text="Clear Seam", clear=True)
    m.sep()
    m.op("mesh.mark_sharp")
    m.op("mesh.mark_sharp", text="Clear Sharp", clear=True)
    m.op("mesh.mark_sharp", text="Mark Sharp from Vertices", use_verts=True)
    m.op("mesh.mark_sharp", text="Clear Sharp from Vertices", use_verts=True, clear=True)
    m.op("mesh.set_sharpness_by_angle")
    if bpy.app.build_options.freestyle:
        m.sep()
        m.op("mesh.mark_freestyle_edge", clear=False)
        m.op("mesh.mark_freestyle_edge", text="Clear Freestyle Edge", clear=True)


def _face(m, context):
    m.op("view3d.edit_mesh_extrude_move_normal", text="Extrude Faces")
    m.op("view3d.edit_mesh_extrude_move_shrink_fatten", text="Extrude Faces Along Normals")
    m.op("mesh.extrude_faces_move", text="Extrude Individual Faces")
    m.sep()
    m.op("mesh.inset")
    m.op("mesh.poke")
    m.op("mesh.quads_convert_to_tris", quad_method='BEAUTY', ngon_method='BEAUTY')
    m.op("mesh.tris_convert_to_quads")
    m.op("mesh.solidify", text="Solidify Faces")
    m.op("mesh.wireframe")
    m.sep()
    m.op("mesh.fill")
    m.op("mesh.fill_grid")
    m.op("mesh.beautify_fill")
    m.sep()
    m.op("mesh.intersect")
    m.op("mesh.intersect_boolean")
    m.sep()
    m.op("mesh.face_split_by_edges")
    m.sep()
    m.op("mesh.faces_shade_smooth")
    m.op("mesh.faces_shade_flat")
    m.sep()
    m.menu("VIEW3D_MT_edit_mesh_faces_data")


# List id -> draw function. Referenced from pie_data "contents".
LISTS = {
    "OBJECT": _object,
    "VIEW": _view,
    "EDIT_MESH": _edit_mesh,
    "VERTEX": _vertex,
    "EDGE": _edge,
    "FACE": _face,
}


def draw_list(layout, context, list_id, width_units=9.45):
    """Draw a list (or a built-in menu idname) in pulldown-menu style."""
    outer = layout.column(align=True)
    outer.emboss = 'NORMAL'          # pies suppress box backgrounds otherwise
    box = outer.box()
    col = box.column(align=True)
    col.emboss = 'PULLDOWN_MENU'     # menu-item look: left-aligned, hover highlight
    col.ui_units_x = width_units
    col.operator_context = 'INVOKE_REGION_WIN'

    fn = LISTS.get(list_id)
    if fn is not None:
        fn(MenuList(col, context), context)
    elif hasattr(bpy.types, list_id):
        col.menu_contents(list_id)
    else:
        col.label(text=list_id + " (missing)", icon='ERROR')
