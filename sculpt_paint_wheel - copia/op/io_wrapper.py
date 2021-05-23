from .. io.io import (
    export_sculpt_toolset_data_to_lib,
    backup_all_addon_data,
    import_sculpt_toolset_data_from_lib,
    UserData,
    reload_global_toolsets,
    reload_active_global_toolset,
    save_active_global_toolset
)

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty

modes_with_custom_toolsets = {'SCULPT'}

from os.path import dirname, abspath, join, exists, isfile, basename
from glob import glob


class IO_OT_export_active_toolset(Operator):
    bl_label = "Export Active Toolset"
    bl_idname = "io.export_active_toolset"
    bl_description = "Export or update active toolset external library"
    
    filename : StringProperty(default="Toolset_Config", name="Filename")
    #export_all : BoolProperty(default=True, name="Export ALL Toolset brushes")
    overwrite : BoolProperty(default=True, name="Overwrite if exist")
    mark_all_as_fake_user : BoolProperty(default=True, name="Mark all as fake user")
    
    @classmethod
    def poll(cls, context):
        return context.mode in modes_with_custom_toolsets
    
    def invoke(self, context, event):
        ts = context.scene.sculpt_wheel.get_active_toolset()
        if not ts:
            return {'CANCELLED'}
        self.filename = ts.name
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        #if context.mode:
        export_sculpt_toolset_data_to_lib(context, self.filename, self.overwrite, False, self.mark_all_as_fake_user)
        return {'FINISHED'}

class IO_OT_export_all_toolsets(Operator):
    bl_label = "Export ALL Toolsets"
    bl_idname = "io.export_all_toolsets"
    bl_description = "Export or update ALL toolsets external libraries"
    
    filename : StringProperty(default="Toolset_Config", name="Filename")
    overwrite : BoolProperty(default=True, name="Overwrite if exist")
    mark_all_as_fake_user : BoolProperty(default=True, name="Mark all as fake user")
    combine_toolsets : BoolProperty(default=False, name="Combine Toolsets")
    export_type : EnumProperty(
        items=(
            ('ALL', 'All', "Export All Toolsets", "", 0),
            ('GLOBAL', 'Global', "Export GLOBAL Toolsets", "WORLD", 1),
            ('LOCAL', 'Local', "Export LOCAL Toolsets", "FILE_BLEND", 2)
        ),
        default='ALL',
        name="Export Type"
    )
    
    @classmethod
    def poll(cls, context):
        return context.mode in modes_with_custom_toolsets
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        #if context.mode:
        export_sculpt_toolset_data_to_lib(context, self.filename, self.overwrite, True, self.mark_all_as_fake_user, self.combine_toolsets, self.export_type)
        return {'FINISHED'}

toolset_lib_list = [("__NONE__", "None", "")]
def search_toolset_libraries(self, context):
    #toolset_lib_list.clear()
    toolset_lib_list = [(f, basename(f), "") for f in glob(join(UserData.EXPORT_SCULPT_TOOLSETS_DIR(), '*.blend'))]
    if toolset_lib_list:
        return toolset_lib_list
    return [("__NONE__", "None", "")]

class IO_OT_import_toolset(Operator):
    bl_label = "Import Toolset"
    bl_idname = "io.import_toolset"
    bl_description = "Import toolset data from external library"
    
    toolset : EnumProperty(
        items=search_toolset_libraries,
        name="Toolset Libraries",
        description="Library of toolsets"
    )
    overwrite : BoolProperty(default=False, name="Overwrite brushes")
    mark_all_as_fake_user : BoolProperty(default=True, name="Mark all as fake user")
    
    @classmethod
    def poll(cls, context):
        return context.mode in modes_with_custom_toolsets
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        if self.toolset == '__NONE__':
            return {'CANCELLED'}
        if not import_sculpt_toolset_data_from_lib(context, self.toolset, self.overwrite, self.mark_all_as_fake_user):
            return {'CANCELLED'}
        return {'FINISHED'}

class IO_OT_backup_all_addon_data(Operator):
    bl_label = "BACKUP ALL Data"
    bl_idname = "io.backup_all_addon_data"
    bl_description = "Export ALL addon data to a backup folder"

    def execute(self, context):
        if not backup_all_addon_data(context):
            return {'CANCELLED'}
        return {'FINISHED'}

class IO_OT_reload_active_global_toolset(Operator):
    bl_label = "Reload Active Toolset"
    bl_idname = "io.reload_active_global_toolset"
    bl_description = "Clear active toolset and reimport it again from external library"
    
    @classmethod
    def poll(cls, context):
        active = context.scene.sculpt_wheel.get_active_toolset()
        return active and active.use_global

    def execute(self, context):
        if not reload_active_global_toolset(context):
            return {'CANCELLED'}
        return {'FINISHED'}

class IO_OT_save_active_global_toolset(Operator):
    bl_label = "Reload Active Toolset"
    bl_idname = "io.save_active_global_toolset"
    bl_description = "Export/Update toolset data on external library"
    
    @classmethod
    def poll(cls, context):
        active = context.scene.sculpt_wheel.get_active_toolset()
        return active and active.use_global

    def execute(self, context):
        if not save_active_global_toolset(context):
            return {'CANCELLED'}
        return {'FINISHED'}

class IO_OT_reload_global_toolsets(Operator):
    bl_label = "Reload Global Toolsets"
    bl_idname = "io.reload_global_toolsets"
    bl_description = "Clear global toolsets and reimport them again from external libraries"

    def execute(self, context):
        if not reload_global_toolsets(context):
            return {'CANCELLED'}
        return {'FINISHED'}
