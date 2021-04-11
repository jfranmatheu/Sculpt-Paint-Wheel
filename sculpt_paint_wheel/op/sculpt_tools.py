from bpy.types import Operator
from bpy.props import StringProperty, IntProperty
from bpy.path import abspath


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
        context.scene.sculpt_wheel.add_toolset(self.name)
        return {'FINISHED'}

class SCULPT_OT_wheel_add_tool(Operator):
    bl_idname = "sculpt.wheel_add_tool"
    bl_label = "Sculpt Wheel: Add Tool"

    tool : StringProperty(name="Tool", default="")

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_wheel.active_toolset != -1

    def execute(self, context):
        from bpy import data as D
        brush = D.brushes.get(tool, None)
        if brush:
            context.scene.sculpt_wheel.get_active_toolset().add_tool(brush)
        return {'FINISHED'}

class SCULPT_OT_wheel_add_active_tool(Operator):
    bl_idname = "sculpt.wheel_add_active_tool"
    bl_label = "Sculpt Wheel: Add Active Tool"
    bl_description = "Add Active Brush/Tool to Active Toolset"

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_wheel.active_toolset != -1

    def execute(self, context):
        from bl_ui.properties_paint_common import UnifiedPaintPanel
        if not UnifiedPaintPanel.paint_settings(context):
            context.scene.sculpt_wheel.get_active_toolset().add_tool(context.workspace.tools.from_space_view3d_mode('SCULPT').idname, False)
            return {'FINISHED'}
        brush = context.tool_settings.sculpt.brush
        if not brush:
            return {'CANCELLED'}
        context.scene.sculpt_wheel.get_active_toolset().add_tool(brush)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_toolset(Operator):
    bl_idname = "sculpt.wheel_remove_toolset"
    bl_label = "Sculpt Wheel: Remove Toolset"

    name : StringProperty(name="Toolset Name", default="")

    def execute(self, context):
        context.scene.sculpt_wheel.remove_toolset(self.name)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_active_toolset(Operator):
    bl_idname = "sculpt.wheel_remove_active_toolset"
    bl_label = "Sculpt Wheel: Remove Active Toolset"
    bl_description = "Remove active toolset"

    def execute(self, context):
        context.scene.sculpt_wheel.remove_toolset(context.scene.sculpt_wheel.active_toolset)
        return {'FINISHED'}

class SCULPT_OT_wheel_remove_tool(Operator):
    bl_idname = "sculpt.wheel_remove_tool"
    bl_label = "Sculpt Wheel: Remove Tool"
    bl_description = "Remove tool"

    tool : StringProperty(name="Tool", default="")
    index : IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT' and context.scene.sculpt_wheel.active_toolset != -1

    def execute(self, context):
        if self.index != -1:
            context.scene.sculpt_wheel.get_active_toolset().remove_tool(self.index)
        elif self.tool:
            context.scene.sculpt_wheel.get_active_toolset().remove_tool(self.tool)
        return {'FINISHED'}

class SCULPT_OT_wheel_activate_toolset(Operator):
    bl_idname = "sculpt.wheel_activate_toolset"
    bl_label = "Sculpt Wheel: Activate Toolset"
    bl_description = "Switch toolset"

    index : IntProperty(name="Toolset Index", default=0)

    def execute(self, context):
        context.scene.sculpt_wheel.active_toolset = self.index
        #context.scene.sculpt_wheel.toolset_list = str(len(toolsets))
        return {'FINISHED'}

class SCULPT_OT_wheel_load_default_tools(Operator):
    bl_idname = "sculpt.wheel_load_default_tools"
    bl_label = "Sculpt Wheel: Load Default Tools"
    bl_description = "Reset toolset to its defaults"

    def execute(self, context):
        ts = context.scene.sculpt_wheel.get_active_toolset()
        if not ts:
            return {'CANCELLED'}
        ts.load_default_tools()
        return {'FINISHED'}
