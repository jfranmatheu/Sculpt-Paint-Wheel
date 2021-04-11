

def is_mesh(ctx):
    return ctx.active_object.type == 'MESH'

def is_gpencil(ctx):
    return ctx.active_object.type == 'GPENCIL'

def is_gpencil_paint(ctx):
    return ctx.mode == 'PAINT_GPENCIL'
