import bpy
''' IMPORTER/EXPORTER FOR WHEEL DATA. '''

from os.path import dirname, abspath, join, exists, isfile, basename, isdir
from ..file_manager import UserData
import json
import re
from .. import bl_info
'''
#user_data_dir = join(dirname(dirname(__file__)), 'user_data')
from .. import gen_config
user_data_dir = str((gen_config() / 'wheel_user_data').absolute())
saved_config_dir = join(user_data_dir, 'saved_config')
export_data_dir = join(user_data_dir, 'export')
global_data_dir = join(user_data_dir, 'shared')
export_sculpt_toolset_dir = join(export_data_dir, 'sculpt_toolsets')
global_sculpt_toolset_dir = join(global_data_dir, 'sculpt_toolsets')
global_sculpt_toolsets_data = join(global_sculpt_toolset_dir, 'toolsets.json')
'''

builtin_brush_names = {'Blob', 'Boundary', 'Clay', 'Clay Strips', 'Clay Thumb', 'Cloth', 'Crease', 'Draw Face Sets', 'Draw Sharp', 'Elastic Deform', 'Fill/Deepen', 'Flatten/Contrast', 'Grab', 'Inflate/Deflate', 'Layer', 'Mask', 'Multi-plane Scrape', 'Multires Displacement Eraser', 'Multires Displacement Smear', 'Nudge', 'Paint', 'Pinch/Magnify', 'Pose', 'Rotate', 'Scrape/Peaks', 'SculptDraw', 'Simplify', 'Slide Relax', 'Smooth', 'Snake Hook', 'Thumb'}

def read_json_file(filepath) -> dict or None:
    with open(filepath, 'r') as f:
        raw_data = f.read()
        if raw_data:
            json_data = json.loads(raw_data)
            if json_data and isinstance(json_data, dict):
                return json_data

def add_sculpt_toolset_to_globals(context, toolset):
    save_global_sculpt_toolset(context, toolset)

def remove_sculpt_toolset_from_globals(context, toolset):
    if not context: context = bpy.context
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    lib_filepath = join(UserData.GLOB_SCULPT_TOOLSETS_DIR(), "%s.blend" % toolset.uuid)
    if exists(lib_filepath) and isfile(lib_filepath):
        from os import remove
        remove(lib_filepath)

    # Read saved toolset data.
    if not exists(data_filepath):
        return False

    data = {}
    with open(data_filepath, 'r') as f:
        raw_data = f.read()
        if raw_data:
            data = json.loads(raw_data)
            if data and isinstance(data, dict) and toolset.uuid in data:
                del data[toolset.uuid]
            else:
                return False
    # Write modified data back to file.
    write_to_file(data, data_filepath)

def update_global_sculpt_toolset_name(context, toolset):
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    data = read_json_file(data_filepath)
    if toolset.uuid in data:
        data[toolset.uuid]['name'] = toolset.name
    write_to_file(data, data_filepath)

def save_global_sculpt_toolset(context, toolset):
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    lib_filepath = join(UserData.GLOB_SCULPT_TOOLSETS_DIR(), "%s.blend" % toolset.uuid)
    #export_sculpt_toolset_data_to_lib(context, toolset.uuid, export_type='GLOBAL')
    bpy.data.libraries.write(lib_filepath, {tool.tool for tool in toolset.tools if not tool.idname}, fake_user=True)
    # Read saved toolset data.
    data = {}
    if not exists(data_filepath):
        #with open(data_filepath, 'w') as f:
        #    f.write("{ }")
        write_to_file(data, data_filepath)
    else:
        with open(data_filepath, 'r') as f:
            raw_data = f.read()
            if raw_data:
                json_data = json.loads(raw_data)
                if json_data and isinstance(json_data, dict):
                    data = json_data
    # Append toolset data to loaded data.
    #data[toolset.uuid] = {'name': toolset.name, 'export_on_save': toolset.export_on_save, 'tools' : [tool.idname for tool in toolset.tools if not tool.tool]}
    data[toolset.uuid] = {
        'name' : toolset.name,
        'blender' : bl_info['blender'],
        'version' : bl_info['version'],
        'export_on_save': toolset.export_on_save,
        #'tools' : [tool.idname for tool in toolset.tools if not tool.tool]
        'tools' : get_tool_list(toolset)
    }
    # Write modified data back to file.
    write_to_file(data, data_filepath)

def get_tool_list(toolset):
    tools = []
    for tool in toolset.tools:
        tools.append(tool.idname if not tool.tool else "@" + tool.tool.name)
    return tools

def save_all_global_sculpt_toolsets(context):
    data = {}
    toolsets = [toolset for toolset in context.scene.sculpt_wheel.toolsets if toolset.export_on_save]
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    for toolset in toolsets:
        lib_filepath = join(UserData.GLOB_SCULPT_TOOLSETS_DIR(), "%s.blend" % toolset.uuid)
        brushes = {tool.tool for tool in toolset.tools if not tool.idname}
        bpy.data.libraries.write(lib_filepath, brushes, fake_user=True)

        # TODO: We need to preserve order, so brushes and tools must be together in the datafile.
        #       and more information should be added as well in a dict form.
        data[toolset.uuid] = {
            'name' : toolset.name,
            'blender' : bl_info['blender'],
            'version' : bl_info['version'],
            'export_on_save': toolset.export_on_save,
            #'tools' : [tool.idname for tool in toolset.tools if not tool.tool]
            'tools' : get_tool_list(toolset)
        }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


def check_global_sculpt_toolsets() -> int:
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    if not exists(data_filepath) or not isfile(data_filepath):
        return 0

    raw_data = ''
    with open(data_filepath, 'r') as f:
        raw_data = f.read()

    if not raw_data:
        return 0

    data: dict = json.loads(raw_data)
    if not data or not isinstance(data, dict):
        return 0

    return len(data)


def load_global_sculpt_toolsets(context, toolsets=None):
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    if not exists(data_filepath):
        print("[SCULPTWHEEL] ERROR: Can't load global sculpt toolsets, file %s not found" % data_filepath)
        return False
    lib_dir = UserData.GLOB_SCULPT_TOOLSETS_DIR()
    from glob import glob
    toolset_libs = glob(join(lib_dir, '*.blend'))
    sculpt_wheel = context.scene.sculpt_wheel

    with open(data_filepath, 'r') as f:
        raw_data = f.read()
        if not raw_data:
            return False

        data = json.loads(raw_data)
        if not data or not isinstance(data, dict):
            return False

        for toolset_lib in reversed(toolset_libs):
            toolset_id = basename(toolset_lib).split('.')[0]
            if toolset_id not in data:
                print("[SCULPTWHEEL] WARN: Toolset %s not in database!" % toolset_id)
                continue
            if sculpt_wheel.has_toolset(toolset_id):
                print("[SCULPTWHEEL] INFO: Toolset %s already in project!" % toolset_id)
                continue

            toolset = sculpt_wheel.add_toolset(data[toolset_id]['name'])
            toolset.prevent_update = True
            toolset.uuid = toolset_id
            toolset.use_global = True
            toolset.export_on_save = data[toolset_id]['export_on_save']
            toolset.prevent_update = False

            ####################################################
            # TOOLSET GENERATION ###############################
            ####################################################

            with bpy.data.libraries.load(toolset_lib, link=False) as (data_from, data_to):
                '''
                if toolset.global_overwrite:
                    for brush in data_from.brushes:
                        d_brush = bpy.data.brushes.get(brush, None)
                        if d_brush:
                            bpy.data.brushes.remove(d_brush)
                '''
                data_to.brushes = data_from.brushes
                #print("DATA FROM BRUSHES:", data_from.brushes)
                #print("DATA TO BRUSHES  :", data_to.brushes)

            # Tiene que ser fuera del with para mantenerse fuera del flujo de E/S y darle tiempo a que se aplique,
            # de forma contraria data_to.brushes sería una lista de str en vez nuestra collection de Brush/es.
            #print("* DATA FROM BRUSHES:", data_from.brushes)
            #print("* DATA TO BRUSHES  :", data_to.brushes)
            tools = data[toolset_id]['tools']
            for tool in tools:
                if tool.startswith('@'):
                    brush_name = tool[1:]
                    # Chequear si es una brush dupli.
                    if brush_name[-4] == '.' and brush_name[-1].isdigit():
                        brush_name = brush_name[:-4]
                    pattern = brush_name + "\.\d\d\d"
                    #print("\t-> Looking for Brush <%s>" % brush_name)
                    for brush in data_to.brushes:
                        #brush = data_to.brushes.get(tool[1:], None)
                        #print("\t\t- <%s> -" % brush.name)
                        if re.search(pattern, brush.name):
                            toolset.add_tool(brush, is_brush=True)
                else:
                    toolset.add_tool(tool, is_brush=False)

    print("[SCULPTWHEEL] Successfully loaded global SculptWheel toolsets from", data_filepath)
    return True


def reload_global_toolsets(context):
    active_brush_name = context.tool_settings.sculpt.brush.name

    # Clear toolsets.
    sculpt_wheel = context.scene.sculpt_wheel
    # Ensure we loop in reserve so remove by index doesn't break the following removes.
    toolset_idx_reversed = len(sculpt_wheel.toolsets) - 1
    for toolset in reversed(sculpt_wheel.toolsets):
        if not toolset.use_global:
            continue
        while toolset.tools:
            toolset.remove_tool(0, True)
        sculpt_wheel.toolsets.remove(toolset_idx_reversed)
        toolset_idx_reversed -= 1

    # Load toolsets.
    load_global_sculpt_toolsets(context)

    # Avoid Void tool/brush.
    if not context.tool_settings.sculpt.brush:
        brush = bpy.data.brushes.get(active_brush_name, None)
        if brush:
            context.tool_settings.sculpt.brush = brush
        else:
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
    context.area.tag_redraw()


def reload_active_global_toolset(context):
    # Clear toolsets.
    sculpt_wheel = context.scene.sculpt_wheel
    toolset = sculpt_wheel.get_active_toolset()
    if not toolset:
        return False

    active_brush_name = context.tool_settings.sculpt.brush.name

    toolset_id = toolset.uuid
    while toolset.tools:
        toolset.remove_tool(0, True)
    sculpt_wheel.toolsets.remove(sculpt_wheel.active_toolset)

    # Load toolsets.
    data_filepath = join(UserData.GLOB_SCULPT_DIR(), "toolsets.json")
    if not exists(data_filepath):
        return False
    lib_dir = UserData.GLOB_SCULPT_TOOLSETS_DIR()
    toolset_lib = join(lib_dir, '%s.blend' % toolset_id)
    sculpt_wheel = context.scene.sculpt_wheel

    with open(data_filepath, 'r') as f:
        raw_data = f.read()
        if not raw_data:
            return False

        data = json.loads(raw_data)
        if not data or not isinstance(data, dict):
            return False

        if toolset_id not in data:
            print("[SCULPTWHEEL] WARN: Toolset %s not in database!" % toolset_id)
            return False
        toolset = sculpt_wheel.add_toolset(data[toolset_id]['name'])
        toolset.prevent_update = True
        toolset.uuid = toolset_id
        toolset.use_global = True
        toolset.export_on_save = data[toolset_id]['export_on_save']
        toolset.prevent_update = False

        '''
        # FORCE OVERWRITE EVEN IF IT HAS NO toolset.globa_overwrite active CAUSE
        if not import_sculpt_toolset_data_from_lib(context, toolset_lib, overwrite=True, mark_fake_user=False, link=False):
            print("[SCULPTWHEEL] ERROR: Can't reload toolset <%s> from database <%s>!" % (toolset.name, toolset_lib))
            return False

        '''
        #import_sculpt_toolset_data_from_lib(context, toolset_lib, overwrite=True, mark_fake_user=False, link=False)
        with bpy.data.libraries.load(toolset_lib, link=False) as (data_from, data_to):
            for brush in data_from.brushes:
                d_brush = bpy.data.brushes.get(brush, None)
                if d_brush:
                    bpy.data.brushes.remove(d_brush)

            data_to.brushes = data_from.brushes

        # Tiene que ser fuera del with para mantenerse fuera del flujo de E/S y darle tiempo a que se aplique,
        # de forma contraria data_to.brushes sería una lista de str en vez nuestra collection de Brush/es.
        tools = data[toolset_id]['tools']
        for tool in tools:
            if tool.startswith('@'):
                brush_name = tool[1:]
                # Chequear si es una brush dupli.
                if brush_name[-4] == '.' and brush_name[-1].isdigit():
                    brush_name = brush_name[:-4]
                pattern = brush_name + "\.\d\d\d"
                #print("\t-> Looking for Brush <%s>" % brush_name)
                for brush in data_to.brushes:
                    #brush = data_to.brushes.get(tool[1:], None)
                    #print("\t\t- <%s> -" % brush.name)
                    if re.search(pattern, brush.name):
                        toolset.add_tool(brush, is_brush=True)
            else:
                toolset.add_tool(tool, is_brush=False)


    if not context.tool_settings.sculpt.brush:
        brush = bpy.data.brushes.get(active_brush_name, None)
        if brush:
            context.tool_settings.sculpt.brush = brush
        else:
            bpy.ops.wm.tool_set_by_id(name="builtin_brush.Draw")
    context.area.tag_redraw()
    return True

def save_active_global_toolset(context):
    # Update export active global toolset.
    sculpt_wheel = context.scene.sculpt_wheel
    toolset = sculpt_wheel.get_active_toolset()
    if not toolset:
        return False
    save_global_sculpt_toolset(context, toolset)

def export_sculpt_toolset_data_to_lib(context, lib_name: str = "", overwrite: bool = True, export_all: bool = False, mark_fake_user: bool = True, export_combined: bool = False, export_type: str = 'ALL'):
    # Get lib path.
    if lib_name and (isfile(lib_name) or isdir(lib_name)) and exists(lib_name):
        ir_dir = isdir(lib_name)
        lib_filepath = lib_name
    else:
        ir_dir = False
        if not lib_name:
            blend_filepath = bpy.data.filepath
            lib_name = bpy.path.basename(blend_filepath)
        elif not lib_name.endswith('.blend'):
            lib_name += ".blend"
        lib_filepath = join(UserData.EXPORT_SCULPT_TOOLSETS_DIR(), lib_name)

        # <---
        if not overwrite and (exists(lib_filepath) or isfile(lib_filepath)):
            temp = lib_name.split('.blend')[0]
            if temp[-1].isdigit():
                num = int(temp[-1]) + 1
                lib_name = temp + str(num)
            else:
                lib_name = temp + "_1.blend"
            lib_filepath = join(UserData.EXPORT_SCULPT_TOOLSETS_DIR(), lib_name)

    # write selected objects and their data to a blend file
    data_blocks = set()
    if export_all:
        if export_type == 'ALL':
            toolsets = context.scene.sculpt_wheel.toolsets
        elif export_type == 'GLOBAL':
            toolsets = [ts for ts in context.scene.sculpt_wheel.toolsets if ts.use_global]
        else:
            toolsets = [ts for ts in context.scene.sculpt_wheel.toolsets if not ts.use_global]
        if export_combined:
            for toolset in toolsets:
                for tool in toolset.tools:
                    data_blocks.add(tool.tool)
                    # This not neccessary but to mark as fake users it is...
                    if mark_fake_user:
                        if tool.tool.texture:
                            data_blocks.add(tool.tool.texture)
        else:
            for toolset in toolsets:
                if ir_dir:
                    out_lib = join(lib_filepath, toolset.name)
                else:
                    out_lib = toolset.name
                export_sculpt_toolset_data_to_lib(context,
                                                  out_lib,
                                                  overwrite=overwrite,
                                                  export_all=False,
                                                  mark_fake_user=mark_fake_user,
                                                  export_combined=False
                                                  )
            return True
    else:
        active_toolset = context.scene.sculpt_wheel.get_active_toolset()
        if not active_toolset:
            return False
        for tool in active_toolset.tools:
            data_blocks.add(tool.tool)
            # This not neccessary but to mark as fake users it is...
            if mark_fake_user:
                if tool.tool.texture:
                    data_blocks.add(tool.tool.texture)

    bpy.data.libraries.write(lib_filepath, data_blocks, fake_user=mark_fake_user)

    return True


def import_sculpt_toolset_data_from_lib(context, lib_name: str = "", overwrite: bool = True, mark_fake_user: bool = True, link: bool = False):
    if not lib_name:
        return False

    # Get lib path.
    if isfile(lib_name) and exists(lib_name):
        lib_filepath = lib_name
    else:
        if not lib_name.endswith('.blend'):
            lib_name += ".blend"
        lib_filepath = join(UserData.EXPORT_SCULPT_TOOLSETS_DIR(), lib_name)
        if not exists(lib_filepath) or not isfile(lib_filepath):
            print("[SCULPTWHEEL] ERROR: Toolset-LIB no found <%s>" % lib_filepath)
            return False

    # Append every brush.
    if overwrite:
        has_brush = context.tool_settings.sculpt.brush is not None
        if has_brush:
            b_name = context.tool_settings.sculpt.brush.name
            b_type = context.tool_settings.sculpt.brush.sculpt_tool

        # NO DUPLICATES.
        with bpy.data.libraries.load(lib_filepath, link=link) as (data_from, data_to):
            # Active brush should be replaced.
            if has_brush:
                has_brush = b_name in data_from.brushes

            for brush in data_from.brushes:
                if brush in builtin_brush_names:
                    continue
                if d_brush := bpy.data.brushes.get(brush, None):
                    bpy.data.brushes.remove(d_brush)
            if mark_fake_user:
                bpy.ops.wm.append(
                    directory=lib_filepath+'/Brush/',
                    files= [{'name': brush} for brush in data_from.brushes if brush not in builtin_brush_names],
                    link=link, set_fake=mark_fake_user)
            else:
                data_to.brushes = {b for b in data_from.brushes if b not in builtin_brush_names}

        if has_brush:# or not context.tool_settings.sculpt.brush:
            if bpy.data.brushes.get(b_name, None):
                bpy.context.tool_settings.sculpt.brush = bpy.data.brushes[b_name]

            '''
            for brush in data_to.brushes:
                if brush.name == b_name:
                    context.tool_settings.sculpt.brush = brush
                    context.area.tag_redraw()
                    break
            '''

    # ALLOW DUPLICATES.
    else:
        with bpy.data.libraries.load(lib_filepath, link=link) as (data_from, data_to):
            if mark_fake_user:
                bpy.ops.wm.append(
                    directory=lib_filepath+'/Brush/',
                    files= [{'name': brush} for brush in data_from.brushes if brush not in builtin_brush_names],
                    link=link, set_fake=mark_fake_user)
            else:
                data_to.brushes = {b for b in data_from.brushes if b not in builtin_brush_names}
                #data_to.brushes = [brush for brush in data_from.brushes if brush not in bpy.data.brushes]

    return data_to.brushes

# EXPORT SCULPT+PAINT CONFIGURATIONS.
'''
1. Create a folder in user_data/saved_config/ based on current date following YYYY_MM_DD naming.
2. Export all toolsets there with following naming {mode}_toolset_{toolset_name}_lib.blend.
3. Export all custom buttons data there with following naming {mode}_custombuttons.json.
4. Export theme config to theme.json
5. Export keymap config to keymap_config.json
6. Export general preferences config to preferences.json
7. Write version txt file.
'''
'''
2020_01_10
    -> SculptWheel
        -> toolset_{toolset_name}.json
        -> buttons.json
    -> PaintWheel
    -> WeightWheel
        -> buttons.kson

'''
def write_to_file(data, filepath):
    import json
    # Serializing data to json.
    json_data = json.dumps(data, indent=4)
    # Write json data to output file.
    with open(filepath, 'w') as out:
        out.write(json_data)


def backup_all_addon_data(ctx):

    ''' 1. Create folder to store data in. '''
    # Check if 'saved_config' folder exists.
    if not exists(UserData.BACKUP_DIR()):
        return False

    # Get Current Date in YYYY_MM_DD format.
    from datetime import datetime
    folder_name = datetime.today().strftime('%Y_%m_%d')

    # Get new data folder path and sub-directories.
    folder_path = join(UserData.BACKUP_DIR(), folder_name)
    sculpt_path = join(folder_path, 'sculpt_wheel')
    paint_path = join(folder_path, 'paint_wheel')
    weight_path = join(folder_path, 'weight_wheel')
    images_path = join(folder_path, 'images')

    # Create folders if root doesn't exist.
    if not exists(folder_path):
        from os import makedirs
        makedirs(folder_path)

        # Create neccessary subfolders.
        makedirs(sculpt_path)
        makedirs(paint_path)
        makedirs(weight_path)
        makedirs(images_path)


    ''' 2. Export toolsets. Naming: {mode}_toolset_{toolset_name}_lib.blend '''
    #####################
    # SculptWheel.      #
    #####################
    data = {}
    data_filepath = join(sculpt_path, "toolsets.json")
    for toolset in ctx.scene.sculpt_wheel.toolsets:
        lib_filepath = join(sculpt_path, "toolset_%s.blend" % toolset.name)
        brushes = {tool.tool for tool in toolset.tools if not tool.idname}
        # This not neccessary (adding brushes it gets rid of textures) but to mark as fake users...
        textures = {tool.tool.texture for tool in toolset.tools if tool.tool.texture != None}
        bpy.data.libraries.write(lib_filepath, brushes.union(textures), fake_user=True)

        tools_data = {}
        for tool in toolset.tools:
            tools_data[tool.tool.name] = {
                'color' : tuple(tool.color),
                'idname' : tool.idname
            }
        data[toolset.uuid] = {
            'name' : toolset.name,
            'export_on_save' : toolset.export_on_save,
            'tools' : tools_data
        }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


    ''' 3. Export custom buttons. Naming: {mode}_pie. '''
    from os.path import basename
    from shutil import copyfile
    #####################
    # SculptWheel.      #
    #####################

    # Get data path.
    data_filepath = join(sculpt_path, 'custom_buttons.json')

    # Construct dictionary and fill with buttons data.
    data = {}
    for button in ctx.scene.sculpt_wheel.custom_buttons:
        b_image_path = button.image_path
        if exists(b_image_path) and isfile(b_image_path):
            # Copy icon to our data folder.
            new_b_image_path = join(images_path, basename(b_image_path))
            if not exists(new_b_image_path):
                copyfile(b_image_path, new_b_image_path)
            b_image_path = new_b_image_path
        else:
            b_image_path = ''
        data[button.name] = {
            'attr' : button.attr,
            'type' : button.type,
            'popup_type' : button.popup_type,
            'image_path' : b_image_path,
            'as_attribute' : button.as_attribute,
            #'preset_menu' : button.preset_menu,
            #'preset_panel' : button.preset_panel,
            #'preset_operator' : button.preset_operator,
            'custom_identifier' : button.custom_identifier,
            'index' : button.index,
            #'show_settings' : button.show_settings
        }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


    ''' 4. Export theme config to theme.json '''
    # Get theme ref. from preferences.
    from ..addon import get_prefs
    prefs = get_prefs(ctx)
    theme = prefs.theme

    # Construct dictionary for theme data and fill it up.
    data_filepath = join(folder_path, 'theme.json')
    data = {
        'base_color' : tuple(theme.base_color),
        'pad_color' : tuple(theme.pad_color),
        'pie_color' : tuple(theme.pie_color)
    }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


    ''' 5. Export keymap config to keymap_config.json '''
    from ..addon.km import get_keyitem_mode, modes

    # Construct dictionary for theme data and fill it up.
    data_filepath = join(folder_path, 'keymap_config.json')
    data = {}
    for mode in modes:
        kmi = get_keyitem_mode(ctx, mode)
        if not kmi:
            continue
        data[mode] = {
            'name' : kmi.name,
            'idname' : kmi.idname,
            'map_type' : kmi.map_type,
            'type' : kmi.type,
            'value' : kmi.value,
            'propvalue' : kmi.propvalue,
            'any' : kmi.any,
            'oskey' : kmi.alt,
            'alt' : kmi.alt,
            'ctrl' : kmi.alt,
            'shift' : kmi.alt,
            'key_modifier' : kmi.key_modifier,
            'repeat' : kmi.repeat,
            'active' : kmi.active
        }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


    ''' 6. Export general preferences config to preferences.json '''
    # Construct dictionary for prefs data and fill it up.
    data_filepath = join(folder_path, 'preferences.json')
    data = {
        'radius' : prefs.radius,
        'show_tool_names' : prefs.show_tool_names,
        'use_custom_tool_colors' : prefs.use_custom_tool_colors,
        'keep_open' : prefs.keep_open,
        'custom_tool_color_mode' : prefs.custom_tool_color_mode,
        'on_release_select' : prefs.on_release_select,
        'gesturepad_mode' : prefs.gesturepad_mode,
        'tool_icon_scale' : prefs.tool_icon_scale
    }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


    ''' 8. Write version. '''
    from .. import bl_info
    with open(join(folder_path, 'version.txt'), 'w') as out:
        out.write(str(bl_info['version']))

    return True


def save_custom_buttons(ctx):
    from os.path import basename
    from shutil import copyfile
    import uuid

    # Get data path.
    folder = UserData.EXPORT_SCULPT_BUTTONS_DIR()
    data_filepath = join(folder, 'custom_buttons.json')
    images_filepath = UserData.EXPORT_SCULPT_BUTTON_ICONS_DIR()

    # Construct dictionary and fill with buttons data.
    data = {}
    for button in ctx.scene.sculpt_wheel.custom_buttons:
        b_image_path = button.image_path
        if exists(b_image_path) and isfile(b_image_path):
            # Copy icon to our data folder.
            new_b_image_path = join(images_filepath, basename(b_image_path))
            if not exists(new_b_image_path):
                copyfile(b_image_path, new_b_image_path)
            b_image_path = new_b_image_path
        else:
            b_image_path = ''
        if button.id == '':
            button.id = uuid.uuid4().hex
        data[button.id] = {
            'name': button.name,
            'attr' : button.attr,
            'type' : button.type,
            'popup_type' : button.popup_type,
            'image_path' : b_image_path,
            'as_attribute' : button.as_attribute,
            'preset_menu' : button.preset_menu,
            'preset_panel' : button.preset_panel,
            'preset_operator' : button.preset_operator,
            'custom_identifier' : button.custom_identifier,
            'index' : button.index,
            #'show_settings' : button.show_settings
        }

    # Write buttons data to datafile.
    write_to_file(data, data_filepath)


def check_sculpt_custom_buttons() -> bool:
    # Get data path.
    folder = UserData.EXPORT_SCULPT_BUTTONS_DIR()
    data_filepath = join(folder, 'custom_buttons.json')

    return exists(data_filepath) and isfile(data_filepath)


def load_custom_buttons(ctx):
    if not check_sculpt_custom_buttons():
        return

    # Get data path.
    folder = UserData.EXPORT_SCULPT_BUTTONS_DIR()
    data_filepath = join(folder, 'custom_buttons.json')

    sculpt_wheel = ctx.scene.sculpt_wheel
    sculpt_wheel.clear_custom_buttons()

    data = read_json_file(data_filepath)
    if not data:
        return

    for but_id, but_data in data.items():
        but = sculpt_wheel.custom_buttons.add()
        but.id = but_id
        for attr, value in but_data.items():
            if not hasattr(but, attr):
                continue
            setattr(but, attr, value)
