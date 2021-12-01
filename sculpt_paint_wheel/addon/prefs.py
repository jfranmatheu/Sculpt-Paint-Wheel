from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import *
from .. import __package__ as main_package


def get_prefs(context):
    return context.preferences.addons[main_package].preferences


class WheelTheme(PropertyGroup):
    base_color: FloatVectorProperty(
        subtype='COLOR', name="Wheel Base Color", min=0, max=1, size=4, default=(.004, .004, .004, .95))
    pie_color: FloatVectorProperty(
        subtype='COLOR', name="Pie Color", min=0, max=1, size=4, default=(.04, .04, .04, .6))
    pad_color: FloatVectorProperty(
        subtype='COLOR', name="PAD Color", min=0, max=1, size=4, default=(.12, .12, .12, .4))
    tool_color: FloatVectorProperty(
        subtype='COLOR', name="PAD Color", min=0, max=1, size=4, default=(.01, .01, .01, .9))
    tool_color_hovered: FloatVectorProperty(
        subtype='COLOR', name="PAD Color", min=0, max=1, size=4, default=(.02, .02, .02, .9))
    tool_outline_color: FloatVectorProperty(
        subtype='COLOR', name="PAD Color", min=0, max=1, size=4, default=(.164, .164, .164, .9))


class ColorPicker(PropertyGroup):
    lock_ring_sv: BoolProperty(name="[Ring] Lock Saturation/Lightness", default=False,
                               description="Lock Saturation and Lightness (Value) in the color picker ring for the Hue")


class WheelPreferences(AddonPreferences):
    bl_idname = main_package

    radius: IntProperty(min=128, default=180, max=300)
    show_tool_names: BoolProperty(default=False)
    use_custom_tool_colors: BoolProperty(default=False)
    keep_open: BoolProperty(default=False)
    custom_tool_color_mode: EnumProperty(
        items=(
            ('RING', "Outline", ""),
            ('FILL', "Background", "")
        ),
        default='RING',
        name="Custom Tool Color Mode"
    )
    on_release_select: BoolProperty(
        default=False, description="Select tool that is under the mouse on key release instead of by LMB clicking on it")
    gesturepad_mode: EnumProperty(
        items=(
            ('PREVIEW', "With Preview", ""),
            ('SIMPLE', "Simplified", "")
        ),
        default='PREVIEW',
        name="Gesture Pad Mode"
    )
    gesturepad_invert: BoolProperty(default=False, name="Invert Gestures",
                                    description="Inverts the gesture PAD size/strength directions")
    tool_icon_scale: FloatProperty(
        min=0.5, max=1.0, default=0.92, name="Tool Icon Scale")

    color_picker: PointerProperty(type=ColorPicker)

    theme: PointerProperty(type=WheelTheme)

    def draw(self, context):
        layout = self.layout
        if not isinstance(self, AddonPreferences):
            self = get_prefs(context)
            is_prefs = False
        else:
            is_prefs = True
        layout.use_property_split = True
        layout.use_property_decorate = False

        #wheel_data = scn.sculpt_wheel

        main_row = layout.row(align=False)

        left_column = main_row.column(align=False)

        settings = left_column.column(align=True)
        header = settings.box()
        header.label(text="Global Settings", icon='WORLD')

        props = settings.box()
        props.prop(self, 'radius', text="Wheel Radius", slider=True)

        if is_prefs or (not is_prefs and context.mode in {'SCULPT', 'PAINT_WEIGHT', 'WEIGHT_GPENCIL'}):
            props.prop(self, 'gesturepad_mode')
            props.prop(self, 'gesturepad_invert',
                       text="Invert Gesture Direction")

            if is_prefs or context.mode == 'SCULPT':
                settings = left_column.column(align=True)
                header = settings.box()
                header.label(text="SculptWheel Settings" if is_prefs else "Tool Settings :",
                             icon='BRUSH_SCULPT_DRAW' if is_prefs else 'TOOL_SETTINGS')

                props = settings.box()
                props.prop(self, 'tool_icon_scale',
                           text="Icon Scale", slider=True)
                props.prop(self, 'show_tool_names', text="Show Tool Names")

                col = props.column(align=True)
                col.prop(self, 'use_custom_tool_colors',
                         text="Custom Tool Color")
                row = col.row()
                row.enabled = self.use_custom_tool_colors
                row.prop(self, 'custom_tool_color_mode', text='')

                props.prop(self, 'on_release_select',
                           text="Select Tool OnRelease")

            if is_prefs or context.mode in {'PAINT_WEIGHT', 'WEIGHT_GPENCIL'}:
                settings = left_column.column(align=True)
                header = settings.box()
                wheel = context.scene.weight_wheel
                header.label(text="WeightWheel Settings", icon='TOOL_SETTINGS')

                props = settings.box()
                props.prop(wheel, 'show_markers')
                props.prop(wheel, 'use_interactable_markers')

                if context.mode == 'PAINT_WEIGHT':
                    props.prop(wheel, 'set_weight_of_selection_directly')
                    props.prop(wheel, 'use_add_substract_brush')

        if not is_prefs and context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_GPENCIL', 'VERTEX_GPENCIL'}:
            # COLOR PICKER PROPERTIES...
            color_picker = self.color_picker

            settings = left_column.column(align=True)
            header = settings.box()
            header.label(text="Color Picker Settings", icon='COLORSET_04_VEC')

            props = settings.box()
            props.use_property_split = False
            props.prop(color_picker, 'lock_ring_sv')

        # kmi = context.window_manager.keyconfigs.addon.keymaps['Sculpt'].keymap_items.get('sculpt.wheel', None)
        if not is_prefs:
            from . km import get_keyitem
            kmi = get_keyitem(context)
            if kmi:
                settings = left_column.column(align=True)
                header = settings.box()
                header.label(text="Keymap Settings", icon='EVENT_RETURN')

                box = settings.box()
                row = box.row()
                row.label(text="Press Key")
                row.template_event_from_keymap_item(kmi)
                row = box.row(align=True)
                row.prop(kmi, 'map_type', text="")
                row.prop(kmi, 'type', text="")
        else:
            from . km import get_keyitem_mode, modes
            right_column = main_row.column(align=False)

            keymap_col = right_column.column(align=True)
            header = keymap_col.box()
            header.label(text="Keymaps", icon='EVENT_RETURN')

            props = keymap_col.box()

            for mode, value in modes.items():
                kmi = get_keyitem_mode(context, mode)
                if kmi:
                    # for attr in dir(kmi):
                    #    print(attr + " -> ", getattr(kmi, attr))
                    box = props.box()
                    box.label(text=value['label'] + " keymap :")
                    row = box.row()
                    row.label(text="Press Key")
                    row.template_event_from_keymap_item(kmi)
                    row = box.row(align=True)
                    row.prop(kmi, 'map_type', text="")
                    row.prop(kmi, 'type', text="")

            settings = keymap_col

            # left_column.separator()

            color_picker_block = left_column.column(align=True)
            header = color_picker_block.box()
            header.label(text="Color Picker", icon='COLORSET_04_VEC')

            color_picker = self.color_picker
            props = color_picker_block.box()
            props.prop(color_picker, 'lock_ring_sv', text="[Ring] Lock SV")

        box = left_column.box()
        box.label(text="Other Settings:")
        box.use_property_split = False
        box.prop(self, 'keep_open', text="Press Again to Close")

        if is_prefs:
            left_column.separator()
            theme_col = left_column.column(align=True)
            header = theme_col.box()
            header.label(text="Theme", icon='RESTRICT_COLOR_ON')

            theme = self.theme
            props = theme_col.box()
            props.prop(theme, 'base_color', text="Base Color")
            props.prop(theme, 'pie_color', text="Pie Color")
            props.prop(theme, 'pad_color', text="PAD Color")

            #layout.operator('io.backup_all_addon_data', text="Back-Up addon data", icon='TEMP')

        '''
        layout = self.layout
        #kmi = context.window_manager.keyconfigs.addon.keymaps['Sculpt'].keymap_items.get('sculpt.wheel', None)
        kmi = context.window_manager.keyconfigs.user.keymaps['Sculpt'].keymap_items.get('sculpt.wheel', None)
        if kmi:
            box = layout.box()
            box.label(text="Keymap :")
            row = box.row()
            row = box.row(align=True)
            row.alignment = 'LEFT'
            row.label(text="Press Key")
            row.template_event_from_keymap_item(kmi)
            row = box.row()
            row.prop(kmi, 'map_type', text="")
            row.prop(kmi, 'type', text="")
        '''

        '''
        keyconfing = context.window_manager.keyconfigs.user    
        keymap = keyconfing.keymaps['Sculpt']
        kmi = keymap.keymap_items.get('sculpt.wheel', None)
        if kmi:
            layout.template_event_from_keymap_item(kmi)
            layout.template_keymap_item_properties(kmi)
        '''
