from bpy.types import Operator
from bpy.props import EnumProperty
from bpy.path import abspath


def change_option(self, context):
    setattr(context.active_object.data, self.option, not getattr(context.active_object.data, self.option))

class WEIGHTWHEEL_OT_box_select_tool_options(Operator):
    bl_idname = "weightwheel.box_select_tool_options"
    bl_label = "Box Select options"
    bl_options = {'UNDO', 'REGISTER'}
    
    option : EnumProperty(
        items=(
            ("use_paint_mask", "Faces", "Face selection masking for weight paint", "FACESEL", 0),
            ("use_paint_mask_vertex", "Vertex", "Vertex selection masking for weight paint", "VERTEXSEL", 1)
        ),
        default="use_paint_mask_vertex",
        update=change_option
    )
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'PAINT_WEIGHT' and context.active_object and 'MESH' in context.active_object.type
    
    def draw(self, context):
        ob_data = context.active_object.data
        row = self.layout.row(align=True)
        row.prop(ob_data, 'use_paint_mask', text="", icon='FACESEL')
        row.prop(ob_data, 'use_paint_mask_vertex', text="", icon='VERTEXSEL')
        #self.layout.row().prop(self, 'option', text="", expand=True)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=80) #width=100) #invoke_props_popup(self, event) #
    
    def execute(self, context):
        setattr(context.active_object.data, self.option, not getattr(context.active_object.data, self.option))
        return {'FINISHED'}
