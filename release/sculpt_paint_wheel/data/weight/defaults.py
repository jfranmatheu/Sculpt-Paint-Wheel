from os.path import dirname, join

icons_dir = join(dirname(dirname(dirname(__file__))), 'images', "custom_buttons")


def_buttons = (
    {
        'name' : "Brush Settings",
        'image_path' : join(icons_dir, 'brush_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_PT_tools_brush_settings_advanced'
    },
    {
        'name' : "Stroke Settings",
        'image_path' : join(icons_dir, 'stroke_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_PT_tools_brush_stroke'
    },
    {
        'name' : "Falloff Settings",
        'image_path' : join(icons_dir, 'fallOff_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_PT_tools_brush_falloff'
    },
    {
        'name' : "Mirror",
        'image_path' : join(icons_dir, 'mirror_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_PT_tools_weightpaint_symmetry_for_topbar'
    },
    {
        'name' : "Weight Options",
        'image_path' : join(icons_dir, 'options_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'PANEL',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_PT_tools_weightpaint_options' #'WEIGHT_PT_options'
    },
    {
        'name' : "Weights",
        'image_path' : join(icons_dir, 'weights_icon.png'),
        'type' : 'POPUP',
        'popup_type' : 'MENU',
        'as_attribute' : 'CUSTOM',
        'custom_identifier' : 'VIEW3D_MT_paint_weight',
        'preset_menu' : 'VIEW3D_MT_paint_weight'
    },
)
