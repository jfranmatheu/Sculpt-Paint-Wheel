modes = {
    'PAINT_TEXTURE' : {
        'label' : 'Texture Paint',
        'km' : 'Image Paint',
        'op' : 'paint.wheel',
    },
    'PAINT_VERTEX' : {
        'label' : 'Vertex Paint',
        'km' : 'Vertex Paint',
        'op' : 'paint.wheel',
    },
    'PAINT_WEIGHT' : {
        'label' : 'Weight Paint',
        'km' : 'Weight Paint',
        'op' : 'weight.wheel',
    },
    'SCULPT' : {
        'label' : 'Sculpt',
        'km' : 'Sculpt',
        'op' : 'sculpt.wheel',
    },
    ### GREASE PENCIL MODES ###
    'PAINT_GPENCIL' : {
        'label' : 'GreasePencil Draw',
        'km' : 'Grease Pencil Stroke Paint Mode',
        'op' : 'paint.wheel', 
    },
    'VERTEX_GPENCIL' : {
        'label' : 'GreasePencil Vertex Paint',
        'km' : 'Grease Pencil Stroke Vertex Mode',
        'op' : 'paint.wheel', 
    },
    'WEIGHT_GPENCIL' : {
        'label' : 'GreasePencil Weight Paint',
        'km' : 'Grease Pencil Stroke Weight Mode',
        'op' : 'weight.wheel', 
    },
    #'SCULPT_GPENCIL' : {
    #    'km' : 'Grease Pencil Stroke Sculpt Mode',
    #    'op' : 'sculpt.wheel', 
    #}
}


def get_keyitem(context):
    return get_keyitem_mode(context, context.mode)

def get_keyitem_mode(context, mode):
    if mode not in modes:
        return None
    mode = modes[mode]
    return context.window_manager.keyconfigs.user.keymaps[mode['km']].keymap_items.get(mode['op'], None)

def register():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for val in modes.values():
        if not cfg.keymaps.__contains__(val['km']):
            cfg.keymaps.new(val['km'], space_type='EMPTY', region_type='WINDOW')
        kmi = cfg.keymaps[val['km']].keymap_items
        kmi.new(val['op'], 'SPACE', 'PRESS')


def unregister():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for val in modes.values():
        if cfg.keymaps.__contains__(val['km']):
            for kmi in cfg.keymaps[val['km']].keymap_items:
                if kmi.idname == val['op']:
                    if kmi.value == 'PRESS' and kmi.type == 'SPACE':
                        cfg.keymaps[val['km']].keymap_items.remove(kmi)
                        break
