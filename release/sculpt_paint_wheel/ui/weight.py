from bpy.types import Panel


class WEIGHT_PT_options(Panel):
    bl_label = "Options"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = 'NONE'
    
    def draw(self, context):
        popover_kw = {"space_type": 'VIEW_3D', "region_type": 'UI', "category": "Tool"}
        self.layout.popover_group(context=".weightpaint", **popover_kw)
