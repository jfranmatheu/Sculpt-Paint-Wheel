modes = (
    'Image Paint',
    'Vertex Paint',
    'Weight Paint',
    'Sculpt'
)
ops = (
    'paint.wheel',
    'paint.wheel',
    'weight.wheel',
    'sculpt.wheel'
)

def get_keyitem(context):
    mode = context.mode
    idx = 0 if mode=='PAINT_TEXTURE' else 1 if mode=='PAINT_VERTEX' else 2 if mode=='PAINT_WEIGHT' else 3
    return context.window_manager.keyconfigs.user.keymaps[modes[idx]].keymap_items.get(ops[idx], None)

def get_keyitem_mode(context, mode):
    idx = 2 if mode=='Weight Paint' else 3 if mode=='Sculpt' else 0
    return context.window_manager.keyconfigs.user.keymaps[mode].keymap_items.get(ops[idx], None)

def register():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for i, mode in enumerate(modes):
        if not cfg.keymaps.__contains__(mode):
            cfg.keymaps.new(mode, space_type='EMPTY', region_type='WINDOW')
        kmi = cfg.keymaps[mode].keymap_items
        kmi.new(ops[i], 'SPACE', 'PRESS')


def unregister():
    from bpy import context as C
    cfg = C.window_manager.keyconfigs.addon
    for i, mode in enumerate(modes):
        if cfg.keymaps.__contains__(mode):
            for kmi in cfg.keymaps[mode].keymap_items:
                if kmi.idname == ops[i]:
                    if kmi.value == 'PRESS' and kmi.type == 'SPACE':
                        cfg.keymaps[mode].keymap_items.remove(kmi)
                        break
