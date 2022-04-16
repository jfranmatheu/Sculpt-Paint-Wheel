import bpy
from bpy.app.handlers import persistent


''' TO INIT GLOBAL TOOLSETS ON .BLEND LOAD. '''
@persistent
def load_handler(dummy):
    load_global_toolsets()
    
def load_global_toolsets():
    print("[Sculpt+Paint Wheel] Loading GLOBAL Toolsets to project {%s}" % bpy.data.filepath)
    from .io import load_global_sculpt_toolsets
    load_global_sculpt_toolsets(bpy.context)


def save_handler(dummy):
    save_global_toolsets()

def save_global_toolsets():
    print("[Sculpt+Paint Wheel] Saving GLOBAL Toolsets...")
    from .io import save_all_global_sculpt_toolsets
    save_all_global_sculpt_toolsets(bpy.context)


def register_handlers():
    ''' TO INIT GLOBAL TOOLSETS ON .BLEND LOAD. '''
    if load_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_handler)
    
    ''' IF SAVE DATA ON PROJECT SAVE. '''
    if save_handler not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(save_handler)

    ''' FOR THE VERSIONING. '''
    #bpy.app.handlers.version_update


def unregister_handlers():
    if load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_handler)
    if save_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(save_handler)
