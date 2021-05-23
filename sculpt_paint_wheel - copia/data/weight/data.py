from bpy.types import PropertyGroup
from bpy.props import *

from .. buttons_management import ButtonsManagement
from .. common import CreateCustomButton, WheelCustomButton


class WeightWheelData(PropertyGroup, ButtonsManagement):
    create_custom_button : PointerProperty(type=CreateCustomButton)
    custom_buttons : CollectionProperty(type=WheelCustomButton)
    
    show_markers : BoolProperty(default=True, name="Show Markers")
    use_interactable_markers : BoolProperty(default=True, name="Interactable Markers")
    
    set_weight_of_selection_directly : BoolProperty(default=True, name="Direct Selection Weight", description="When changing weight value will directly update the weight of the selection mask")

    use_add_substract_brush : BoolProperty(default=False, name="Add/Substract Brush Toggle", description="Instead of 'Draw' brush will use Add/Substract brushes in the brush tool")

    def load_default_custom_buttons(self):
        from . defaults import def_buttons
        super().load_default_custom_buttons(def_buttons)
