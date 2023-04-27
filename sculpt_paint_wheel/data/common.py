from bpy.types import PropertyGroup, Brush, Image
from bpy.props import *
from bpy import ops as OP
from os.path import isfile, join, dirname
from . sculpt.presets import preset_menus, preset_operators, preset_panels
import bpy

from sculpt_paint_wheel.props import Props

blender_icons_path = join(dirname(dirname(__file__)), 'images', 'blender', 'tile234.png')


def get_tool_index(tool):
    return tool.index


class WheelColorPicker(PropertyGroup):
    type : EnumProperty(
        items = (
            ('SV_RECT', "SV Rectangle", "Rectangle to control Saturation and Value plus a ring to control Hue"),
            ('HS_CIRC', "HS Circle", "Circle to control Hue and Saturation plus a slider to control Value"),
        ),
        default='SV_RECT',
        name="Color Picker Type"
    )
    use_slice : BoolProperty(default=False, name="Slice Color Picker")

    def show_context_menu(self):
        OP.wm.call_panel(name="SCULPTWHEEL_PT_show_color_picker_context_menu", keep_open=True)

class Tool:
    def __init__(self, tool) -> None:
        self.tool = tool
        self.is_brush = not isinstance(str, tool)

class WheelTool(PropertyGroup):
    def update_tool(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        if self.tool:
            if not self.tool.use_paint_sculpt:
                self.tool = self.prev_tool
                return
            elif self.prev_tool == self.tool:
                return
            self.name = self.tool.name
            self.prev_tool = self.tool
        elif self.idname == '':
            sculpt_wheel.get_active_toolset().remove_tool(self.name) # Change to self
    
    def update_name(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        # name = self.idname.split('.')[1].replace('_', ' ').capitalize()
        if (self.idname != '' and not self.tool) and (not self.name or self.name == ''):
            sculpt_wheel.get_active_toolset().remove_tool(self.name)

    name : StringProperty(name="Name", default="Tool", options={'TEXTEDIT_UPDATE'}, update=update_name)
    color : FloatVectorProperty(subtype='COLOR', name="Color", min=0, max=1, size=4, default=(.2, .2, .2, 1))
    tool : PointerProperty(type=Brush, update=update_tool)
    prev_tool : PointerProperty(type=Brush)
    idname : StringProperty()
    order : IntProperty(name="Index-Order", default=0, min=0)

    def show_context_menu(self):
        if not self.tool:
            return
        OP.wm.call_panel(name="SCULPTWHEEL_PT_show_tool_context_menu", keep_open=True)


def update_global(self, context):
    if self.prevent_update:
        return
    if self.use_global:
        from ..spw_io import add_sculpt_toolset_to_globals
        add_sculpt_toolset_to_globals(context, self)
        for tool in self.tools:
            if tool.tool:
                tool.tool.use_fake_user = False
    else:
        from ..spw_io import remove_sculpt_toolset_from_globals
        remove_sculpt_toolset_from_globals(context, self)
        for tool in self.tools:
            if tool.tool:
                tool.tool.use_fake_user = True

def update_toolset_name(self, context):
    if self.prevent_update or not self.use_global:
        return
    from ..spw_io import update_global_sculpt_toolset_name
    update_global_sculpt_toolset_name(context, self)


class WheelToolset(PropertyGroup):
    name : StringProperty(name="Name", default="Toolset", update=update_toolset_name)
    tools : CollectionProperty(type=WheelTool)
    use_global : BoolProperty(default=False,
                              name="Global Toolset",
                              description="Share toolset between all your projects.",
                              update=update_global
                              )

    active_tool : IntProperty(default=-1)
    uuid : StringProperty(default="", name="UUID")

    prevent_update : BoolProperty(default=True)
    export_on_save : BoolProperty(default=False, description="Save toolset data when saving .blend file (Ctrl+S)")
    use_defaults : BoolProperty(default=False)
    #global_overwrite : BoolProperty(default=False, description="Global brushes will over-write blendfile brushes that match the name")

    def load_default_tools(self, copy: bool = True):
        from bpy import data as D
        from . sculpt.defaults import def_tools
        from ..spw_io import builtin_brush_names
        if self.use_defaults:
            for tool in self.tools:
                if tool.tool and tool.tool.name not in builtin_brush_names and 'default' in tool.tool:
                    D.brushes.remove(tool.tool)
        self.tools.clear()
        for data in def_tools:
            br = D.brushes.get(data[0], None)
            if br is None:
                continue
            if copy:
                new_br = br.copy()
                new_name = 'SW | ' + br.name
                new_br.name = new_name
                while new_br.name != new_name:
                    D.brushes.remove(D.brushes.get(new_name))
                    new_br.name = new_name
            else:
                new_br = br
            new_br['default'] = 1
            tool = self.add_tool(new_br, is_brush=True)
            if tool and data[1]:
                # tool.name = data[1]
                tool.name = new_br.name
        self.use_defaults = True

    def add_tool(self, tool, is_brush=True):
        order = (len(self.tools) - 1)
        if is_brush:
            if not isinstance(tool, Brush):
                return
            if not tool.use_paint_sculpt:
                return
            if tool.use_custom_icon and (not tool.icon_filepath or not isfile(tool.icon_filepath)):
                return
            if self.search_tool(tool):
                return
            new_tool = self.tools.add()
            new_tool.name = tool.name
            new_tool.tool = tool
            new_tool.prev_tool = tool
            tool['order'] = order
        else:
            if not tool:
                return
            new_tool = self.tools.add()
            new_tool.idname = tool
            new_tool.name = tool.split('.')[1].replace('_', ' ').capitalize()
        
        new_tool.order = order
        return new_tool

    def get_tool(self, name):
        return self.tools.get(name, None)

    def get_active_tool(self):
        return self.tools[self.active_tool]

    def check_tool(self, tool):
        if isinstance(tool, int):
            num_tools = len(self.tools)
            return tool <= num_tools - 1 and tool != -1

    def select_tool(self, ctx, index):
        if self.tools[index].idname != '':
            OP.wm.tool_set_by_id(name=self.tools[index].idname)
        else:
            OP.wm.tool_set_by_id(name="builtin_brush.Draw")
            ctx.tool_settings.sculpt.brush = self.tools[index].tool

    def swap_tools(self, t1, t2):
        #from .. utils import swap
        '''
        n = len(self.tools)
        if t1 < 0 or t2 > n:
            return
        if t2 < 0 or t2 > n:
            return
        '''
        # self.tools[t1], self.tools[t2] = self.tools[t2], self.tools[t1]
        temp_tool = self.tools[t1].tool
        temp_name = self.tools[t1].name
        temp_index = self.tools[t1].order

        if self.tools[t1].tool:
            self.tools[t1].tool['order'] = self.tools[t2].order
        if self.tools[t2].tool:
            self.tools[t2].tool['order'] = temp_index
        self.tools[t1].order = self.tools[t2].order
        self.tools[t2].order = temp_index

        self.tools[t1].tool = self.tools[t2].tool
        self.tools[t1].name = self.tools[t2].name
        self.tools[t2].tool = temp_tool
        self.tools[t2].name = temp_name

        #swap(self.tools[t1].tool, self.tools[t2].tool)
        #swap(self.tools[t1].name, self.tools[t2].name)

    def get_tool_index(self, name):
        i = 0
        for t in self.tools:
            if t.name == name:
                return i
            i += 1
        return -1

    def remove_tool(self, tool, remove_brush_datablock: bool = False):
        if isinstance(tool, int):
            if tool != -1:
                if remove_brush_datablock and self.tools[tool].tool:
                    try:
                        bpy.data.brushes.remove(self.tools[tool].tool)
                    except:
                        pass
                self.tools.remove(tool)
        elif isinstance(tool, str):
            self.remove_tool(self.get_tool_index(tool))

        self.ensure_tool_indices()

    def search_tool(self, tool):
        for t in self.tools:
            if t.tool == tool:
                return True
        return False

    def show_tool_context_menu(self, idx: int):
        if idx == -1:
            return
        if idx >= len(self.tools):
            return
        self.active_tool = idx
        self.tools[idx].show_context_menu()

    def ensure_tool_indices(self):
        for idx, tool in enumerate(self.tools):
            tool['order'] = tool.order = idx

    def sort_tools(self):
        """ Sort tools using their index. """
        tools = [Tool(t.tool if t.tool else t.idname) for t in self.tools]


class CreateCustomButton(PropertyGroup):
    name : StringProperty(default="Button", name="Name")
    type : EnumProperty(
        items=(
            ('POPUP', "Pop-up", "Trigger this button to popup a menu"),
            ('OPERATOR', "Operator", "Trigger this button to execute some command/operator"),
            # ('TOGGLE', "Toggle", "Trigger this button to toggle on/off some BRUSH property")
        ),
        default='OPERATOR'
    )
    popup_type : EnumProperty(
        items=(
            ('MENU', "Menu", ""),
            ('PANEL', "Panel", ""),
            #('PIE_MENU', "Pie Menu", "")
        ),
        default='PANEL'
    )
    image_path : StringProperty(default=blender_icons_path, name="Image Path", subtype='FILE_PATH')
    as_attribute : EnumProperty(
        items=(
            ('CUSTOM', "Custom", "Manually enter your attribute"),
            ('PRESET', "Preset", "Select a preset")
        ),
        default='PRESET',
        name="As Attribute..."
    )
    preset_menu : EnumProperty(
        items=preset_menus,
        default='VIEW3D_MT_mask',
        name="Menu"
    )
    preset_panel : EnumProperty(
        items=preset_panels,
        default='VIEW3D_PT_tools_brush_falloff',
        name="Panel"
    )
    preset_operator : EnumProperty(
        items=preset_operators,
        default='object.voxel_remesh',
        name="Operator"
    )
    custom_identifier : StringProperty(default="", name="Identifier")


class WheelCustomButton(CreateCustomButton, PropertyGroup):
    id: StringProperty(default="", options={'HIDDEN'})
    name : StringProperty(default="Button", name="Name")
    attr : StringProperty(default="", name="Attribute")
    type : EnumProperty(
        items=(
            ('POPUP', "Pop-up", "Trigger this button to popup a menu"),
            ('OPERATOR', "Operator", "Trigger this button to execute some command/operator"),
            ('TOGGLE', "Toggle", "Trigger this button to toggle on/off some BRUSH property")
        ),
        default='OPERATOR'
    )
    popup_type : EnumProperty(
        items=(
            ('MENU', "Menu", ""),
            ('PANEL', "Panel", ""),
            #('PIE_MENU', "Pie Menu", "")
        ),
        default='PANEL'
    )
    image_path : StringProperty(default='', name="Image Path", subtype='FILE_PATH')
    as_attribute : EnumProperty(
        items=(
            ('CUSTOM', "Custom", "Manually enter your attribute"),
            ('PRESET', "Preset", "Select a preset")
        ),
        default='PRESET',
        name="As Attribute..."
    )
    preset_menu : EnumProperty(
        items=preset_menus,
        default='VIEW3D_MT_mask',
        name="Menu"
    )
    preset_panel : EnumProperty(
        items=preset_panels,
        default='VIEW3D_PT_tools_brush_falloff',
        name="Panel"
    )
    preset_operator : EnumProperty(
        items=preset_operators,
        default='object.voxel_remesh',
        name="Operator"
    )
    custom_identifier : StringProperty(default="", name="Identifier")

    index : IntProperty(default=-1, min=0)
    show_settings : BoolProperty(default=False, name="Show Settings")

    def __call__(self, context=None):
        #print(self.attr)
        if self.type == 'POPUP':
            try:
                if self.popup_type == 'MENU':
                    return OP.wm.call_menu(name=self.attr)
                elif self.popup_type == 'PANEL':
                    return OP.wm.call_panel(name=self.attr, keep_open=True)
                elif self.popup_type == 'PIE_MENU':
                    return OP.wm.call_menu_pie(name=self.attr)
            except Exception as e:
                print(e)
            return
        elif self.type == 'OPERATOR':
            OP.ed.undo_push(message=self.attr)
            try:
                exec(self.attr)
                #OP.sculptwheel.run_custom_op(ops=self.attr)
                OP.ed.undo_push(message=self.attr)
            except RuntimeError:
                print("Runtime Error")
            except Exception as e:
                print(e)
        elif self.type == 'TOGGLE':
            if not context:
                context = bpy.context
            brush = context.tool_settings.sculpt.brush
            if not brush:
                return
            if not hasattr(brush, self.attr):
                return
            setattr(brush, self.attr, not getattr(brush, self.attr))
