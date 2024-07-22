import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.path import abspath
from bpy_extras.io_utils import ExportHelper, ImportHelper
from ..file_manager import UserData

from ..props import Props


class SCULPTWHEEL_OT_run_custom_op(Operator):
    bl_idname = "sculptwheel.run_custom_op"
    bl_label = "Sculpt Wheel: Add Toolset"
    bl_options = {'UNDO', 'REGISTER'}
    ops : StringProperty(default="")
    def execute(self, context):
        if self.ops:
            exec(self.ops)
        return {'FINISHED'}
    
class SCULPT_OT_wheel_add_toolset(Operator):
    bl_idname = "sculpt.wheel_add_toolset"
    bl_label = "Sculpt Wheel: Add Toolset"
    bl_description = "Add new toolset and mark as active"
    #bl_options = {'REGISTER', 'UNDO'}

    name : StringProperty(name="Toolset Name", default="")

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.add_toolset(self.name)
        return {'FINISHED'}

class SCULPT_OT_wheel_add_tool(Operator):
    bl_idname = "sculpt.wheel_add_tool"
    bl_label = "Sculpt Wheel: Add Tool"

    tool : StringProperty(name="Tool", default="")

    @classmethod
    def poll(cls, context):
        sculpt_wheel = Props.SculptWheelData(context)
        return context.mode == 'SCULPT' and sculpt_wheel.active_toolset != -1

    def execute(self, context):
        from bpy import data as D
        brush = D.brushes.get(self.tool, None)
        if brush:
            sculpt_wheel = Props.SculptWheelData(context)
            sculpt_wheel.get_active_toolset().add_tool(brush)
        return {'FINISHED'}

class SCULPT_OT_wheel_add_active_tool(Operator):
    bl_idname = "sculpt.wheel_add_active_tool"
    bl_label = "Sculpt Wheel: Add Active Tool"
    bl_description = "Add Active Brush/Tool to Active Toolset"

    @classmethod
    def poll(cls, context):
        sculpt_wheel = Props.SculptWheelData(context)
        return context.mode == 'SCULPT' and sculpt_wheel.active_toolset != -1

    def execute(self, context):
        # Add non-brush tool.
        sculpt_wheel = Props.SculptWheelData(context)
        from bl_ui.properties_paint_common import UnifiedPaintPanel
        if not UnifiedPaintPanel.paint_settings(context):
            sculpt_wheel.get_active_toolset().add_tool(context.workspace.tools.from_space_view3d_mode('SCULPT').idname, False)
            return {'FINISHED'}
        # Add brush tool.
        brush = context.tool_settings.sculpt.brush
        if not brush:
            return {'CANCELLED'}
        sculpt_wheel.get_active_toolset().add_tool(brush)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_toolset(Operator):
    bl_idname = "sculpt.wheel_remove_toolset"
    bl_label = "Sculpt Wheel: Remove Toolset"

    name : StringProperty(name="Toolset Name", default="")

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.remove_toolset(self.name)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_active_toolset(Operator):
    bl_idname = "sculpt.wheel_remove_active_toolset"
    bl_label = "Sculpt Wheel: Remove Active Toolset"
    bl_description = "Remove active toolset"

    remove_globally : BoolProperty(name="Remove Globally", default=True)

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.remove_toolset(sculpt_wheel.active_toolset, self.remove_globally)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_tool(Operator):
    bl_idname = "sculpt.wheel_remove_tool"
    bl_label = "Sculpt Wheel: Remove Tool"
    bl_description = "Remove tool"

    tool : StringProperty(name="Tool", default="")
    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        sculpt_wheel = Props.SculptWheelData(context)
        return context.mode == 'SCULPT' and sculpt_wheel.active_toolset != -1

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        if self.index != -1:
            sculpt_wheel.get_active_toolset().remove_tool(self.index)
        elif self.tool:
            sculpt_wheel.get_active_toolset().remove_tool(self.tool)
        return {'FINISHED'}

class SCULPT_OT_wheel_activate_toolset(Operator):
    bl_idname = "sculpt.wheel_activate_toolset"
    bl_label = "Sculpt Wheel: Activate Toolset"
    bl_description = "Switch toolset"

    index : IntProperty(name="Toolset Index", default=0)

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.active_toolset = self.index
        #sculpt_wheel.toolset_list = str(len(toolsets))
        return {'FINISHED'}

class SCULPT_OT_wheel_toolset_mark_as_global(Operator):
    bl_idname = "sculpt.wheel_toolset_mark_as_global"
    bl_label = "Sculpt Wheel: Mark as Global Toolset"
    bl_description = "Mark Active Toolset as Global"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.get_active_toolset()
        if not ts or ts.use_global:
            return {'CANCELLED'}
        ts.use_global = True
        import bpy
        bpy.ops.io.save_active_global_toolset()
        return {'FINISHED'}


class SCULPT_OT_wheel_toolset_mark_as_local(Operator):
    bl_idname = "sculpt.wheel_toolset_mark_as_local"
    bl_label = "Sculpt Wheel: Mark as Local Toolset"
    bl_description = "Mark Active Toolset as Local"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.get_active_toolset()
        if not ts or not ts.use_global:
            return {'CANCELLED'}
        ts.use_global = False
        # import bpy
        # bpy.ops.io.save_active_global_toolset()
        return {'FINISHED'}


class SCULPT_OT_wheel_load_default_tools(Operator):
    bl_idname = "sculpt.wheel_load_default_tools"
    bl_label = "Sculpt Wheel: Load Default Tools"
    bl_description = "Reset toolset to its defaults"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.get_active_toolset()
        if not ts:
            return {'CANCELLED'}
        ts.load_default_tools()
        return {'FINISHED'}


class SCULPT_OT_wheel_create_default_toolset(Operator):
    bl_idname = "sculpt.wheel_create_default_toolset"
    bl_label = "Sculpt Wheel: Initialize Default Toolset"
    bl_description = "Initialize Default Toolset"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.add_toolset("Default")
        if not ts:
            return {'CANCELLED'}
        ts.load_default_tools()
        return {'FINISHED'}


class SCULPT_OT_wheel_init_toolsets(Operator):
    bl_idname = "sculpt.wheel_init_toolsets"
    bl_label = "Sculpt Wheel: Initialize Toolsets"
    bl_description = "Initialize Toolsets (global if available)"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        from ..spw_io import check_global_sculpt_toolsets, load_global_sculpt_toolsets
        if sculpt_wheel.global_toolset_count() == 0 and check_global_sculpt_toolsets() > 0:
            load_global_sculpt_toolsets(context)
            if sculpt_wheel.get_active_toolset() is not None:
                return {'FINISHED'}
            else:
                # Something failed!
                pass
        import bpy
        bpy.ops.sculpt.wheel_create_default_toolset()
        return {'FINISHED'}


class SCULPT_OT_wheel_export_active_toolset(Operator, ExportHelper):
    ''' REMAKED! '''
    bl_label = "Export Active Toolset as Library"
    bl_idname = "sculpt.wheel_export_active_toolset"
    bl_description = "Export or update active brush toolset external library"

    #filename : StringProperty(default="Toolset_Config", name="Filename")
    #export_all : BoolProperty(default=True, name="Export ALL Toolset brushes")
    #overwrite : BoolProperty(default=True, name="Overwrite if exist")
    use_fake_user : BoolProperty(default=True, name="Mark all as fake user")

    filename_ext: str = ".blend"

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def invoke(self, context, event):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.get_active_toolset()
        if not ts:
            return {'CANCELLED'}
        # self.filename = ts.name
        # Initialize filepath.
        filename = ts.name + ".blend"
        self.filepath = UserData.EXPORT_SCULPT_TOOLSETS_DIR(filename)
        return super().invoke(context, event)
        #    return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        active_toolset = sculpt_wheel.get_active_toolset()
        if not active_toolset:
            return {'CANCELLED'}
        data_blocks = set()
        for tool in active_toolset.tools:
            if tool.tool is None:
                continue
            data_blocks.add(tool.tool)
            if tool.tool.texture is None:
                continue
            data_blocks.add(tool.tool.texture)

        if not data_blocks:
            return {'CANCELLED'}
        bpy.data.libraries.write(self.filepath, data_blocks, fake_user=self.use_fake_user)
        #export_sculpt_toolset_data_to_lib(context, self.filepath, self.overwrite, False, self.mark_all_as_fake_user)
        return {'FINISHED'}


class SCULPT_OT_wheel_import_toolset(Operator, ExportHelper):
    ''' REMAKED! '''
    bl_label = "Import Brush Library"
    bl_idname = "sculpt.wheel_import_toolset"
    bl_description = "Import Brush Library and create a new toolset with the brushes"

    #filename : StringProperty(default="Toolset_Config", name="Filename")
    #export_all : BoolProperty(default=True, name="Export ALL Toolset brushes")
    overwrite : BoolProperty(default=False, name="Overwrite if exist")
    use_fake_user : BoolProperty(default=False, name="Use fake user")

    filename_ext: str = ".blend"
    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def invoke(self, context, event):
        sculpt_wheel = Props.SculptWheelData(context)
        ts = sculpt_wheel.get_active_toolset()
        if not ts:
            return {'CANCELLED'}
        # self.filename = ts.name
        # Initialize filepath.
        self.filepath = UserData.EXPORT_SCULPT_TOOLSETS_DIR(ts.name + ".blend")
        return super().invoke(context, event)
        #    return context.window_manager.invoke_props_dialog(self, width=300)

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        lib_filepath: str = self.filepath
        from ..spw_io import builtin_brush_names, isfile, exists, basename
        if not lib_filepath or not exists(lib_filepath) or not isfile(lib_filepath) or not lib_filepath.endswith('.blend'):
            return {'CANCELLED'}
        filtered_brushes = []
        with bpy.data.libraries.load(lib_filepath) as (data_from, data_to):
            filtered_brushes = [b for b in data_from.brushes if b not in builtin_brush_names]
            data_to.brushes = filtered_brushes
        '''
        from ..spw_io import import_sculpt_toolset_data_from_lib
        brushes = import_sculpt_toolset_data_from_lib(context, self.filepath, overwrite=self.overwrite, mark_fake_user=self.use_fake_user, link=False)
        if brushes:
            from os.path import basename
            filename = basename(self.filepath)
            ts = sculpt_wheel.add_toolset(filename, force=True)
            for brush_name in brushes:
                if brush := bpy.data.brushes.get(brush_name, None):
                    ts.add_tool(brush, is_brush=True)
        '''
        if data_to.brushes:
            if self.overwrite:
                for brush in filtered_brushes:
                    if brush.name in bpy.data.brushes:
                        bpy.data.brushes.remove(brush)
            filename = basename(lib_filepath)
            ts = sculpt_wheel.add_toolset(filename, force=True)
            for brush in data_to.brushes:
                if brush is not None:
                    ts.add_tool(brush, is_brush=True)
                    brush.use_fake_user = self.use_fake_user
        return {'FINISHED'}
