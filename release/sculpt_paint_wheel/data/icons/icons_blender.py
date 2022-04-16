from os import listdir
from os.path import exists, join, isfile, dirname
import bpy


def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items # [('NONE', "None", "")]

    wm = context.window_manager
    directory = dirname(__file__)

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory == pcoll.my_previews_dir:
        return pcoll.my_previews

    #print("Scanning directory: %s" % directory)
    # Scan the directory for png files
    i = 0
    for fn in listdir(directory):
        if fn.lower().endswith(".png"):
            # generates a thumbnail preview for a file.
            filepath = join(directory, fn)
            icon = pcoll.get(fn)
            if not icon:
                thumb = pcoll.load(fn, filepath, 'IMAGE')
            else:
                thumb = pcoll[fn]
            enum_items.append((fn, fn, "", thumb.icon_id, i))
            i += 1

    pcoll.my_previews = enum_items
    return pcoll.my_previews


# We can store multiple preview collections here,
# however in this example we only store "main"
preview_collections = {}


def register():
    from bpy.types import WindowManager
    from bpy.props import EnumProperty

    WindowManager.sculpt_wheel_icons = EnumProperty (
        items=enum_previews_from_directory_items,
        name="Icons"
    )

    # Note that preview collections returned by bpy.utils.previews
    # are regular Python objects - you can use them to store custom data.
    #
    # This is especially useful here, since:
    # - It avoids us regenerating the whole enum over and over.
    # - It can store enum_items' strings
    #   (remember you have to keep those strings somewhere in py,
    #   else they get freed and Blender references invalid memory!).
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews_dir = ""
    pcoll.my_previews = ()

    preview_collections["main"] = pcoll


def unregister():
    from bpy.types import WindowManager

    del WindowManager.sculpt_wheel_icons

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
