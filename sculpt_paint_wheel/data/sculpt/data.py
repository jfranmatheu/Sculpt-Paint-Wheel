from bpy.types import PropertyGroup, Brush, Image, UILayout
from bpy.props import *
from bpy import ops as OP
from data.tools_io import ToolsIO
from . presets import *
from os.path import isfile, join, dirname
from bpy.path import abspath
from .. tools_management import ToolsManagement
from .. buttons_management import ButtonsManagement
from .. common import WheelToolset, CreateCustomButton, WheelCustomButton, WheelColorPicker
#from . dat_weight import WeightWheelData

def get_enum_desc(data, attr):
    return UILayout.enum_item_description(data, attr, getattr(data, attr))

toolset_items = [("NONE", "None", "", "", 0)]
def toolset_list_items(self, context):
    if not self.toolsets:
        return [("NONE", "None", "", "", 0)]
    toolset_items.clear()
    
    for i, toolset in enumerate(self.toolsets):
        toolset_items.append(
            (
                str(i),
                toolset.name,
                "",
                "WORLD" if toolset.use_global else "FILE_BLEND",
                i
            )
        )
    toolset = self.get_active_toolset()
    if toolset_items:
        return toolset_items
    return [("NONE", "None", "", "", 0)]

def update_toolset_list(self, context):
    if self.toolset_list == 'NONE':
        return
    OP.sculpt.wheel_activate_toolset(index=int(self.toolset_list))


class SculptWheelData(PropertyGroup, ToolsManagement, ButtonsManagement, ToolsIO):
    # pos : IntVectorProperty(min=0, name="Position") # managed by operator (mouse pos.)
    num_tools : IntProperty(min=8, default=8, max=16, name="Number of Tools")
    toolsets : CollectionProperty(type=WheelToolset)
    active_toolset : IntProperty(min=-1, default=-1)
    toolset_list : EnumProperty(
        name="Active Toolset",
        description="Active Toolset",
        items=toolset_list_items,
        update=update_toolset_list
    )

    create_custom_button : PointerProperty(type=CreateCustomButton)
    custom_buttons : CollectionProperty(type=WheelCustomButton)

    color_picker : PointerProperty(type=WheelColorPicker)

    def load_default_custom_buttons(self):
        from . defaults import def_buttons
        super().load_default_custom_buttons(def_buttons)
