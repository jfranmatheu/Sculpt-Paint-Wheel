from bpy.types import Operator
from bpy.props import StringProperty, IntProperty
from bpy.path import abspath

from ..props import Props


class SCULPT_OT_wheel_add_customm_button(Operator):
    bl_idname = "sculpt.wheel_add_custom_button"
    bl_label = "Sculpt Wheel: Add Custom Button"
    bl_description = "Create a custom button for SculptWheel"

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        create = sculpt_wheel.create_custom_button
        if not create.name or create.name.isspace():
            self.report({'WARNING'}, "Button name is not valid")
            return {'CANCELLED'}
        from os.path import isfile
        image_path = create.image_path
        if image_path.startswith('//'):
            image_path = abspath(image_path)
        if not image_path or not isfile(image_path):
            self.report({'WARNING'}, "Image path is not valid")
            return {'CANCELLED'}
        if create.as_attribute == 'CUSTOM':
            if create.custom_identifier == "" or create.custom_identifier.isspace():
                return {'CANCELLED'}
            if create.type == 'POPUP':
                if create.popup_type == 'PANEL':
                    if '_PT_' not in create.custom_identifier:
                        self.report({'WARNING'}, "Panel Identifier is not valid")
                        return {'CANCELLED'}
                elif create.popup_type == 'MENU':
                    if '_MT_' not in create.custom_identifier:
                        self.report({'WARNING'}, "Menu Identifier is not valid")
                        return {'CANCELLED'}
                elif create.popup_type == 'PIE_MENU':
                    pass
                try:
                    command = "from bpy.types import " + create.custom_identifier
                    exec(command)
                except Exception as e:
                    print(e)
                    self.report({'WARNING'}, "Identifier is not valid")
                    return {'CANCELLED'}
            elif create.type == 'OPERATOR':
                split = create.custom_identifier.split('(')
                if not split[0].startswith('bpy.ops.'):
                    self.report({'WARNING'}, "Operator call doesn't start with 'bpy.ops.'")
                try:
                    import bpy
                    if not eval(split[0]):
                        self.report({'WARNING'}, "Operator call is not valid")
                        return {'CANCELLED'}
                except Exception as e:
                    print(e)
                    self.report({'WARNING'}, "Operator call is not valid")
                    return {'CANCELLED'}
                if not '(' in create.custom_identifier:
                    create.custom_identifier += '()'
            elif create.type == 'TOGGLE':
                self.report({'WARNING'}, "Toggle support is still in development")
                return {'CANCELLED'}
                if not hasattr(context.tool_settings.sculpt.brush, create.custom_identifier):
                    return {'CANCELLED'}
        sculpt_wheel.add_custom_button(create)
        return {'FINISHED'}


class SCULPT_OT_wheel_remove_custom_button(Operator):
    bl_idname = "sculpt.wheel_remove_custom_button"
    bl_label = "Sculpt Wheel: Remove Custom Button"
    bl_description = "Remove this custom button"

    index : IntProperty(name="Custom Button Index", default=-1)

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def execute(self, context):
        if self.index == -1:
            return {'CANCELLED'}
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.remove_custom_button(self.index)
        return {'FINISHED'}


class SCULPT_OT_wheel_load_default_custom_buttons(Operator):
    bl_idname = "sculpt.wheel_load_default_custom_buttons"
    bl_label = "Sculpt Wheel: Load Default Custom Buttons"
    bl_description = "Load Default SculptWheel Custom Buttons"

    def execute(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        sculpt_wheel.remove_all_custom_buttons()
        sculpt_wheel.load_default_custom_buttons()
        return {'FINISHED'}


class SCULPT_OT_wheel_load_custom_buttons(Operator):
    bl_idname = "sculpt.wheel_load_custom_buttons"
    bl_label = "Sculpt Wheel: Load Custom Buttons"
    bl_description = "Load/Reset SculptWheel Custom Buttons"

    def execute(self, context):
        from ..spw_io import check_sculpt_custom_buttons, load_custom_buttons
        if check_sculpt_custom_buttons():
            load_custom_buttons(context)
        else:
            import bpy
            bpy.ops.sculpt.wheel_load_default_custom_buttons()
        return {'FINISHED'}


class SCULPT_OT_wheel_save_custom_buttons(Operator):
    bl_idname = "sculpt.wheel_save_custom_buttons"
    bl_label = "Sculpt Wheel: Save Custom Buttons"
    bl_description = "Save SculptWheel Custom Buttons"

    def execute(self, context):
        from ..spw_io import save_custom_buttons
        save_custom_buttons(context)
        return {'FINISHED'}
