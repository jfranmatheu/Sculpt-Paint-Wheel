from bpy.types import Panel
from bl_ui.properties_paint_common import brush_settings

from ..props import Props


class SculptWheelTool_ContextMenu(Panel):
    bl_idname = "SCULPTWHEEL_PT_show_tool_context_menu"
    bl_label = "Tool Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "NONE"

    def draw(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        toolset = sculpt_wheel.get_active_toolset()
        if not toolset:
            return
        tool  = toolset.get_active_tool().tool
        if not tool:
            return

        brush_settings(self.layout, context, tool, True)

class SculptWheel_ActiveToolset_Options(Panel):
    bl_idname = "SCULPTWHEEL_PT_show_toolset_options"
    bl_label = "Active Toolset Options"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "NONE"

    def draw(self, context):
        sculpt_wheel = Props.SculptWheelData(context)
        toolset = sculpt_wheel.get_active_toolset()
        if not toolset:
            return

        box = self.layout.box()

        box.prop(toolset, 'name', text="Name")
        box.prop(toolset, 'use_global', text="Global Toolset (beta)", toggle=False)
        box.alert = True
        box.label(text="Toolset is GLOBAL" if toolset.use_global else "Toolset is LOCAL", icon="WORLD" if toolset.use_global else "FILE_BLEND")

        if toolset.use_global:
            box = self.layout.box()
            row = box.row()
            row.operator('io.save_active_global_toolset', text="Save", icon='FILE_TICK') # (export changes)
            row.operator("io.reload_active_global_toolset", text="Reload", icon='FILE_REFRESH')
            box.prop(toolset, 'export_on_save', text="Save on project save")
            #box.prop(toolset, 'global_overwrite', text="Overwrite brushes on (re)load")
            #box.operator('io.export_active_toolset', text="Reload (import changes)", icon='FILE_REFRESH')

        box = self.layout.box()
        box.operator('sculpt.wheel_export_active_toolset', text="Export as Library", icon='EXPORT')
        #box.operator('io.export_active_toolset', text="Export as Library", icon='EXPORT')

        box = self.layout.box()
        box.alert = True
        box.label(text="Danger Zone", icon='ERROR')
        row = box.row(align=False)
        if toolset.use_defaults and not toolset.use_global:
            row.operator('sculpt.wheel_load_default_tools', text="Reset Default", icon='FILE_REFRESH')
        if toolset.use_global:
            col = box.column(align=True)
            col.operator('sculpt.wheel_remove_active_toolset', text="Remove Locally", icon='TRASH').remove_globally = False
            col.operator('sculpt.wheel_remove_active_toolset', text="Remove Globally", icon='TRASH').remove_globally = True
        else:
            row.operator('sculpt.wheel_remove_active_toolset', text="Remove", icon='TRASH')

        row = self.layout.row()
        row.enabled = False
        row.label(text="ID: %s" % toolset.uuid)


class SculptWheel_Toolsets_GeneralOptions(Panel):
    bl_idname = "SCULPTWHEEL_PT_show_general_toolset_options"
    bl_label = "General Toolset Options"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "NONE"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        box = col.box()
        box.label(text="Toolset Management", icon='ASSET_MANAGER')
        box = col.box()
        box.operator('io.reload_global_toolsets', text="Reload GLOBAL Toolsets", icon='FILE_REFRESH')

        col = layout.column(align=True)
        box = col.box()
        box.label(text="Toolset Library - Import/Export", icon='OUTPUT')
        box = col.box()
        #box.operator('io.export_active_toolset', text="Export ACTIVE Toolset", icon='EXPORT')
        #box.operator('io.export_all_toolsets', text="Export ALL Toolsets", icon='EXPORT')
        #box.operator('io.import_toolset', text="Import Toolset", icon='IMPORT')
        box.operator('sculpt.wheel_export_active_toolset', text="Export ACTIVE Toolset as Library", icon='EXPORT')
        box.operator('sculpt.wheel_import_toolset', text="Import Library as Toolset", icon='IMPORT')
