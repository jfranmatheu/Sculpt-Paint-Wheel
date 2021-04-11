preset_menus = (
    ('VIEW3D_MT_sculpt', "Sculpt Menu", "Header's 'Sculpt' menu"),
    ('VIEW3D_MT_mask', "Mask Menu", "Header's 'Mask' menu"),
    ('VIEW3D_MT_face_sets', "Face Sets Menu", "Header's 'Face Sets' menu")
)

preset_panels = (
    ('VIEW3D_PT_tools_brush_settings_advanced', "Advanced Settings", "Brush Advanced Settings"),
    ('VIEW3D_PT_tools_brush_stroke', "Stroke", "Popover for stroke settings"),
    ('VIEW3D_PT_tools_brush_falloff', "Falloff", "Popover for falloff settings"),
    ('VIEW3D_PT_tools_brush_display', "Display", "Popover for display settings"),
    ('VIEW3D_PT_sculpt_symmetry_for_topbar', "Symmetry", "Popover for symmetry settings"),
    ('VIEW3D_PT_sculpt_dyntopo', "Dyntopo", "Popover for Dyntopo settings"),
    ('VIEW3D_PT_sculpt_voxel_remesh', "Remesh", "Popover for remesh settings"),
    ('VIEW3D_PT_sculpt_options', "Options", "Popover for sculpt options"),
    ('VIEW3D_PT_sculpt_context_menu', "Context Menu", "Popover for sculpt context menu"),
    ('VIEW3D_PT_tools_brush_texture', "Texture", "Popover for brush texture settings"),
    ('VIEW3D_PT_shading', "Shading", "Popover for shading settings"),
    ('VIEW3D_PT_shading_lighting', "Shading Lighning (Matcap...)", "Popover for shading lighting settings as matcap or studio"),
    ('VIEW3D_PT_tools_active', "Tools", "Popover for toolbar tools"),
    #('VIEW3D_PT_tools_brush_swatches', "Color Palette", "Popover for swatches (color palette)")
)

preset_operators = (
    ("_MASK_INVERT",    "Invert Mask",              "paint.mask_flood_fill#mode='INVERT'"),
    ("_MASK_CLEAR",     "Clear Mask",               "paint.mask_flood_fill#mode='VALUE', value=0"),
    ("_MASK_ALL",       "Mask All",                 "paint.mask_flood_fill#mode='VALUE', value=1"),
    ("_MF_SMOOTH",      "Smooth Mask",              "sculpt.mask_filter#filter_type='SMOOTH', auto_iteration_count=True"),
    ("_MF_SHARPEN",     "Sharpen Mask",             "sculpt.mask_filter#filter_type='SHARPEN', auto_iteration_count=True"),
    ("_MF_GROW",        "Grow Mask",                "sculpt.mask_filter#filter_type='GROW', auto_iteration_count=True"),
    ("_MF_SHRINK",      "Shrink Mask",              "sculpt.mask_filter#filter_type='SHRINK', auto_iteration_count=True"),
    ("_MORE_CONTRAST",  "+ Contrast Mask",          "sculpt.mask_filter#filter_type='CONTRAST_INCREASE', auto_iteration_count=True"),
    ("_LESS_CONTRAST",  "- Contrast Mask",          "sculpt.mask_filter#filter_type='CONTRAST_DECREASE', auto_iteration_count=True"),
    ("_MASK_EXTRACT",   "Mask Extract",             'mesh.paint_mask_extract'),
    ("_MASK_SLICE",     "Mask Slice",               'mesh.paint_mask_slice#fill_holes=False, new_object=False'),
    ("_MASK_SLICE_FILL","Mask Slice + Fill Holes",  'mesh.paint_mask_slice#new_object=False'),
    ("_MASK_SLICE_NEW", "Mask Slice to New Object", 'mesh.paint_mask_slice'),
    ("_MASK_DIRTY",     "Dirty Mask",               'sculpt.dirty_mask'),
    ("sculpt.face_sets_create#mode='MASKED'", "FaceSet from Mask", ""),
    ("sculpt.face_sets_create#mode='VISIBLE'", "FaceSet from Visible", ""),
    ("sculpt.face_set_change_visibility#mode='INVERT'", "Invert Visible FaceSets", ""),
    ("sculpt.face_set_change_visibility#mode='SHOW_ALL'", "Show All FaceSets", ""),
    ("sculpt.face_sets_randomize_colors", "Random FaceSets colors", ""),
    ('object.voxel_remesh', "Voxel Remesh", ""),
    ('object.quadriflow_remesh', "Quad Remesh", ""),
    ('_HIDE_ALL',       "Hide Masked", "paint.hide_show#area='MASKED'"),
    ('_UNHIDE_ALL',     "Unhide All", "paint.hide_show#action='SHOW', area='ALL'"),
    ('object.multires_subdivide', "Subdivide", ""),
    ('object.multires_higher_levels_delete', "Delete Higher", "Delete Higher Subdiv Levels"),
    ('sculpt.symmetrize',"Symmetrize", ""),
    ('brush.add',       "Add Brush", ""),
    ('brush.reset',     "Reset Brush", ""),
    ("_PIVOT_ORIGIN",   "Pivot to origin", "sculpt.set_pivot_position#mode='ORIGIN'"),
    ("_PIVOT_UNMASKED", "Pivot to unmasked", "sculpt.set_pivot_position#mode='UNMASKED'"),
    ("_PIVOT_BORDER", "Pivot to mask border", "sculpt.set_pivot_position#mode='BORDER'"),
    ("_PIVOT_ACTIVE", "Pivot to active vertex", "sculpt.set_pivot_position#mode='ACTIVE'"),
    ("_PIVOT_SURFACE", "Pivot to surface under cursor", "sculpt.set_pivot_position#mode='SURFACE'"),
    ('sculpt.optimize', "Optimize", ""),
)