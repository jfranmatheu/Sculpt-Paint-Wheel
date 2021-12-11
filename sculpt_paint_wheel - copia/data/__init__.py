from . sculpt.data import SculptWheelData
from . weight.data import WeightWheelData


def register(reg):
    from bpy.props import PointerProperty, IntProperty
    from bpy.types import Scene as scn, Brush
    scn.sculpt_wheel = PointerProperty(type=SculptWheelData)
    scn.weight_wheel = PointerProperty(type=WeightWheelData)
    Brush.toolset_id = IntProperty(default=-1)

def unregister(unreg):
    from bpy.types import Scene as scn, Brush
    del scn.sculpt_wheel
    del scn.weight_wheel
    del Brush.toolset_id

'''
from . common import CreateCustomButton, WheelCustomButton, WheelColorPicker, WheelTool, WheelToolset

classes = (
    WheelTool, CreateCustomButton, WheelCustomButton, WheelColorPicker, WheelToolset, SculptWheelData, WeightWheelData
)

def register(reg):
    from bpy.props import PointerProperty, IntProperty
    from bpy.types import Scene as scn, Brush
    for cls in classes:
        reg(cls)
    scn.sculpt_wheel = PointerProperty(type=SculptWheelData)
    scn.weight_wheel = PointerProperty(type=WeightWheelData)
    Brush.toolset_id = IntProperty(default=-1)

def unregister(unreg):
    for cls in reversed(classes):
        unreg(cls)
    from bpy.types import Scene as scn, Brush
    del scn.sculpt_wheel
    del scn.weight_wheel
    del Brush.toolset_id
'''
