from os.path import dirname, join

icons_dir = join(dirname(dirname(dirname(__file__))), 'images', "custom_buttons")

def_tools = (
    ('SculptDraw', 'Sculpt Draw'),
    ('Draw Sharp', None),
    ('Clay Strips', None),
    ('Inflate/Deflate', 'Inflate'),
    ('Crease', None),
    ('Scrape/Peaks', 'Scrape'),
    ('Multi-plane Scrape', 'MultiPlane Scrape'),
    ('Pinch/Magnify', 'Pinch'),
    ('Grab', None),
    ('Elastic Deform', None),
    ('Pose', None),
    ('Cloth', None),
    ('Mask', None),
    ('Draw Face Sets', None)
)

def_buttons = (
    #{
    #    'name' : "Advanced Brush Settings",
    #    'image_path' : join(icons_dir, 'brush_icon.png'),
    #    'type' : 'POPUP',
    #    'popup_type' : 'PANEL',
    #    'as_attribute' : 'PRESET',
    #    'preset_panel' : 'VIEW3D_PT_tools_brush_stroke'
    #},
    {
        'name' : "Stroke Settings",
        'image_path' : join(icons_dir, 'stroke_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'PRESET',
        'preset_panel' : 'VIEW3D_PT_tools_brush_stroke'
    },
    {
        'name' : "Falloff Settings",
        'image_path' : join(icons_dir, 'fallOff_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'PRESET',
        'preset_panel' : 'VIEW3D_PT_tools_brush_falloff'
    },
    {
        'name' : "Texture Settings",
        'image_path' : join(icons_dir, 'texture_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'PRESET',
        'preset_panel' : 'VIEW3D_PT_tools_brush_texture'
    },
    {
        'name' : "Remesh Settings",
        'image_path' : join(icons_dir, 'grid_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'PRESET',
        'preset_panel' : 'VIEW3D_PT_sculpt_voxel_remesh'
    },
    {
        'name' : "Mask Clear",
        'image_path' : join(icons_dir, 'maskClear_icon.png'),
        'type' : 'OPERATOR',
        'as_attribute' : 'PRESET',
        'preset_operator' : '_MASK_CLEAR',
        'custom_identifier' : "paint.mask_flood_fill#mode='VALUE', value=0"
    },
    {
        'name' : "Mask Invert",
        'image_path' : join(icons_dir, 'maskInvert_icon.png'),
        'type' : 'OPERATOR',
        'as_attribute' : 'PRESET',
        'preset_operator' : '_MASK_INVERT',
        'custom_identifier' : "paint.mask_flood_fill#mode='INVERT'"
    },
    {
        'name' : "Mask Sharp",
        'image_path' : join(icons_dir, 'maskSharp_icon.png'),
        'type' : 'OPERATOR',
        'as_attribute' : 'PRESET',
        'preset_operator' : '_MF_SHARPEN',
        'custom_identifier' : "sculpt.mask_filter#filter_type='SHARPEN', auto_iteration_count=True"
    },
    {
        'name' : "Mask Smooth",
        'image_path' : join(icons_dir, 'maskSmooth2_icon.png'),
        'type' : 'OPERATOR',
        'as_attribute' : 'PRESET',
        'preset_operator' : '_MF_SMOOTH',
        'custom_identifier' : "sculpt.mask_filter#filter_type='SMOOTH', auto_iteration_count=True"
    }
)
