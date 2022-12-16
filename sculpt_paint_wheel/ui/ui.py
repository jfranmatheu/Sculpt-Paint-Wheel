from bpy.types import Panel, UILayout, Brush, UIList # SCULPT_PT_Wheel
# from .. panel import SculptWheelPanel
from .. addon.prefs import WheelPreferences, get_prefs
from bpy.props import *
from .. icons import Icon

'''
class SculptWheelBasePanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Sculpt'
'''

class SculptWheelPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Sculpt'

    bl_idname = "SCULPT_PT_wheel"
    bl_label = "Sculpt Wheel"

    @classmethod
    def poll(cls, context):
        return context.mode == 'SCULPT'

    def draw(self, context):
        pass

class PaintWheelPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = ".paint_common"
    bl_category = 'Paint'

    bl_idname = "PAINT_PT_wheel"
    bl_label = "Paint Wheel"

    @classmethod
    def poll(cls, context):
        return context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_GPENCIL', 'VERTEX_GPENCIL'}

    def draw(self, context):
        WheelPreferences.draw(self, context)

class WeightWheelPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_context = ".paint_common"
    bl_category = 'Weight'

    bl_idname = "WEIGHT_PT_wheel"
    bl_label = "Weight Wheel"

    @classmethod
    def poll(cls, context):
        return context.mode in {'PAINT_WEIGHT', 'WEIGHT_GPENCIL'}

    def draw(self, context):
        WheelPreferences.draw(self, context)

class SCULPTWHEEL_UL_toolset_slots(UIList):
    # Custom properties, saved with .blend file.
    use_filter_empty: BoolProperty(
        name="Filter Empty",
        default=False,
        options=set(),
        description="Whether to filter empty vertex groups",
    )
    use_filter_empty_reverse: BoolProperty(
        name="Reverse Empty",
        default=False,
        options=set(),
        description="Reverse empty filtering",
    )
    use_filter_name_reverse: BoolProperty(
        name="Reverse Name",
        default=False,
        options=set(),
        description="Reverse name filtering",
    )
    use_filter_show : BoolProperty(
        name="Show Filters",
        default=False,
        options=set(),
        description="Show filtering options",
    )
    
    # The draw_item function is called for each item of the collection that is visible in the list.
    #   data is the RNA object containing the collection,
    #   item is the current drawn item of the collection,
    #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
    #   have custom icons ID, which are not available as enum items).
    #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
    #   active item of the collection).
    #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
    #   index is index of the current item in the collection.
    #   flt_flag is the result of the filtering process for this item.
    #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
    #         need them.
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # data == toolset
        # item == tool
        tool = item
        custom_col = get_prefs(context).use_custom_tool_colors
        # draw_item must handle the three layout types... Usually 'DEFAULT' and 'COMPACT' can share the same code.
        
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        #elif self.layout_type in {'DEFAULT', 'COMPACT'}:
        
        # You should always start your row layout by a label (icon + text), or a non-embossed text field,
        # this will also make the row easily selectable in the list! The later also enables ctrl-click rename.
        # We use icon_value of label, as our given icon is an integer value, not an enum ID.
        # Note "data" names should never be translated!
        if custom_col:
            layout = layout.row(align=True)
            color = layout.row(align=True)
            color.ui_units_x = .75
            color.prop(tool, "color", text="")
        if tool.idname:
            layout.prop(tool, "name", text="")# , emboss=False)
        else:
            layout.prop(tool, "tool", text="", icon_value=UILayout.icon(tool.tool))
    
    '''
    def draw_filter(self, context, layout):
        # Nothing much to say here, it's usual UI code...
        row = layout.row()

        subrow = row.row(align=True)
        subrow.prop(self, "filter_name", text="")
        subrow.prop(self, "use_filter_name_reverse", text="", icon='ARROW_LEFTRIGHT')
        
        row = row.row()
        row.alignment = 'RIGHT'
        row.operator('sculpt.wheel_add_active_tool', text="Add Brush", icon='ADD')
    '''


class SculptWheelToolsets(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Sculpt'

    bl_parent_id = 'SCULPT_PT_wheel'
    bl_label = 'Toolsets'
    bl_idname = "SCULPT_PT_wheel_toolsets"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        wheel_data = scn.sculpt_wheel

        if wheel_data.active_toolset == -1 or (active_toolset := wheel_data.get_active_toolset()) is None:
            #layout.label(text="Create a toolset to start:")
            #layout.operator('sculpt.wheel_add_toolset', text="Create Toolset")
            from ..spw_io import check_global_sculpt_toolsets
            if (global_toolset_count := check_global_sculpt_toolsets()) > 0:
                layout.label(text="Global toolsets detected ! (" + str(global_toolset_count) + ')')
                row = layout.row()
                row.scale_y = 2.5
                row.operator('io.reload_global_toolsets', text="Load GLOBAL Toolsets", icon='IMPORT')
            else:
                layout.label(text="Initialize Default Toolset")
                row = layout.row()
                row.scale_y = 2.5
                row.operator('sculpt.wheel_create_default_toolset', text="Initialize", icon='FILE_REFRESH')
            return

        main_col = layout.column(align=True)
        
        toolset_row = main_col.row(align=True)
        
        toolset_row.operator('sculpt.wheel_add_toolset', text="", icon='PRESET_NEW') # New ToolSet
        toolset_row.prop(wheel_data, 'toolset_list', text="", icon="WORLD" if active_toolset.use_global else "FILE_BLEND")
        
        toolset_row.popover('SCULPTWHEEL_PT_show_toolset_options', text="", icon='PROPERTIES')
        
        toolset_row.label(text="", icon='BLANK1')
        
        toolset_row.popover('SCULPTWHEEL_PT_show_general_toolset_options', text="", icon='COLLAPSEMENU')
        
        #main_col.label(text=active_toolset.name)
        main_col.template_list("SCULPTWHEEL_UL_toolset_slots", "", active_toolset, "tools", active_toolset, "active_tool", type='DEFAULT') #, type='GRID', columns=3)

        row = main_col.row(align=True)
        row.alignment = 'RIGHT'
        row.operator('sculpt.wheel_add_active_tool', text="Add Active Brush", icon='ADD')


class SculptWheelCustomButtons(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Sculpt'

    bl_parent_id = 'SCULPT_PT_wheel'
    bl_label = 'Custom Buttons'
    bl_idname = "SCULPT_PT_wheel_custom_buttons"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 2

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        wheel_data = scn.sculpt_wheel
        create = wheel_data.create_custom_button
        buttons = wheel_data.custom_buttons

        if len(buttons) == 0:
            from ..spw_io import check_sculpt_custom_buttons
            if check_sculpt_custom_buttons():
                layout.operator('sculpt.wheel_load_custom_buttons', text="Load Buttons")
            else:
                layout.operator('sculpt.wheel_load_custom_buttons', text="Initialize Default Buttons")
            layout.scale_y = 2.5
            return

        if len(buttons) != 0:
            box = layout.box().column(align=True)
            box.use_property_split = True
            box.use_property_decorate = False
            box.label(text="List :", icon="OUTLINER")
            box.separator()
        for i, b in enumerate(buttons):
            row = box.row(align=True)
            # row.prop(b, 'show_settings', text="", icon='TRIA_RIGHT' if not b.show_settings else 'TRIA_DOWN')
            row.prop(b, 'name', text="")
            row.operator('sculpt.wheel_remove_custom_button', text="", icon="X").index = i
            if b.show_settings:
                sett = box.box()
                sett.prop(b, 'image_path', text="Image Path")
                #sett.template_icon_view(context.window_manager, "sculpt_wheel_icons")
                sett.prop(b, 'type', text="Type")
                if b.type == 'POPUP':
                    sett.prop(b, 'popup_type', text="Pop-up Type")
                    _row = sett.row()
                    _row.prop(b, 'as_attribute', text="Use...", expand=True)
                    if b.as_attribute == 'PRESET':
                        if b.popup_type == 'MENU':
                            sett.prop(b, 'preset_menu', text="Presets")
                        elif b.popup_type == 'PANEL':
                            sett.prop(b, 'preset_panel', text="Presets")
                        elif b.popup_type == 'PIE_MENU':
                            # sett.prop(b, 'popup_type', text="Identifier") # TODO: Some presets for pie menus?
                            sett.alert = True
                            sett.label(text="No presets for pie menus :(")
                    elif b.as_attribute == 'CUSTOM':
                        sett.prop(b, 'custom_identifier', text="Idname")
                elif b.type == 'OPERATOR':
                    _row = sett.row()
                    _row.prop(b, 'as_attribute', text="Use...", expand=True)
                    if b.as_attribute == 'PRESET':
                        sett.prop(b, 'preset_operator', text="Presets")
                    elif b.as_attribute == 'CUSTOM':
                        sett.prop(b, 'custom_identifier', text="Operator")
                        sett.label(text="Example: bpy.ops.object.voxel_remesh()")
                elif b.type == 'TOGGLE':
                    sett.alert = True
                    sett.label(text="Work in progress...")

                    #_row = sett.row()
                    #_row.prop(create, 'as_attribute', text="Use...", expand=True)
                    #if create.as_attribute == 'PRESET':
                    #    sett.label(text="No presets for toggles :(")
                    #elif create.as_attribute == 'CUSTOM':
                    #    sett.prop(create, 'custom_identifier', text="Property Name")

                box.separator()

        box = layout.box().column(align=True)
        box.use_property_split = True
        box.use_property_decorate = False
        box.label(text="Create :", icon="PROPERTIES")
        box.separator()
        sett = box.box()
        sett.prop(create, 'name', text="Name")
        sett.prop(create, 'image_path', text="Image Path")
        #sett.template_icon_view(context.window_manager, "sculpt_wheel_icons")
        sett.prop(create, 'type', text="Type")
        if create.type == 'POPUP':
            sett.prop(create, 'popup_type', text="Pop-up Type")
            _row = sett.row()
            _row.prop(create, 'as_attribute', text="Use...", expand=True)
            if create.as_attribute == 'PRESET':
                if create.popup_type == 'MENU':
                    sett.prop(create, 'preset_menu', text="Presets")
                elif create.popup_type == 'PANEL':
                    sett.prop(create, 'preset_panel', text="Presets")
                elif create.popup_type == 'PIE_MENU':
                    # sett.prop(b, 'popup_type', text="Identifier") # TODO: Some presets for pie menus?
                    sett.alert = True
                    sett.label(text="No presets for pie menus :(")
            elif create.as_attribute == 'CUSTOM':
                sett.prop(create, 'custom_identifier', text="Idname")
        elif create.type == 'OPERATOR':
            _row = sett.row()
            _row.prop(create, 'as_attribute', text="Use...", expand=True)
            if create.as_attribute == 'PRESET':
                sett.prop(create, 'preset_operator', text="Presets")
            elif create.as_attribute == 'CUSTOM':
                sett.prop(create, 'custom_identifier', text="Operator")
                sett.label(text="Example: bpy.ops.object.voxel_remesh()")
        elif create.type == 'TOGGLE':
            sett.alert = True
            sett.label(text="Work in progress...")

            #_row = sett.row()
            #_row.prop(create, 'as_attribute', text="Use...", expand=True)
            #if create.as_attribute == 'PRESET':
            #    sett.label(text="No presets for toggles :(")
            #elif create.as_attribute == 'CUSTOM':
            #    sett.prop(create, 'custom_identifier', text="Property Name")

        box.operator('sculpt.wheel_add_custom_button', text="Create Button")
        
        box = layout.box()
        row = box.row()
        row.operator('sculpt.wheel_save_custom_buttons', text="S A V E")
        row.operator('sculpt.wheel_load_custom_buttons', text="R E S E T")
        row = box.row()
        row.operator('sculpt.wheel_load_default_custom_buttons', text="Reset to default")


class SculptWheelSettings(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Sculpt'

    bl_parent_id = 'SCULPT_PT_wheel'
    bl_label = 'Wheel Settings'
    bl_idname = "SCULPT_PT_wheel_settings"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    def draw(self, context):
        WheelPreferences.draw(self, context)


from . weight import WEIGHT_PT_options
from . sculpt import SculptWheelTool_ContextMenu, SculptWheel_ActiveToolset_Options, SculptWheel_Toolsets_GeneralOptions
classes = (
    SCULPTWHEEL_UL_toolset_slots,
    WeightWheelPanel,
    PaintWheelPanel,
    SculptWheelPanel,
    SculptWheelToolsets,
    SculptWheelCustomButtons,
    SculptWheelSettings,
    WEIGHT_PT_options,
    SculptWheelTool_ContextMenu,
    SculptWheel_ActiveToolset_Options,
    SculptWheel_Toolsets_GeneralOptions
)

def register(reg):
    for cls in classes:
        reg(cls)

def unregister(unreg):
    for cls in reversed(classes):
        unreg(cls)
