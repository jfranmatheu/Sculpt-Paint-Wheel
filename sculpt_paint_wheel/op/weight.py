import bpy
from bl_ui.properties_paint_common import UnifiedPaintPanel
from bpy.types import Operator
from .. px.weight import *
from mathutils import Color, Vector
from math import cos, sin, tan, pi, degrees, atan, floor
#from .. gui_types.button import ButtonCircle
from .. data.icons import get_button_icon, get_tool_icon, ButtonIcon, DefToolImage as ToolIcon
from .. utils import * #Cursor, CursorIcon, rotate_point_around_point
from .. addon import get_prefs
from math import radians
from .. gui_types.toolbar import Toolbar
from bl_ui.properties_paint_common import UnifiedPaintPanel


weight_toolbar = Toolbar(rows_cols=2)
weight_toolbar.tool('Draw',     'Draw',         True,   ToolIcon.PAINT_DRAW, set())
weight_toolbar.tool('Blur',     'Blur',         True,   ToolIcon.PAINT_BLUR, set(), {'offset':Vector((0, -10))})
weight_toolbar.tool('Average',  'Average',      True,   ToolIcon.PAINT_AVERAGE, set(), {'offset':Vector((0, -10))})
weight_toolbar.tool('Smear',    'Smear',        True,   ToolIcon.PAINT_SMEAR, set())
weight_toolbar.tool('Gradient', 'gradient',     False,  ToolIcon.PAINT_GRADIENT, set())
weight_toolbar.tool('Sample Weight',   'sample_weight',False,  ToolIcon.PAINT_SAMPLE_WEIGHT, set(), {'offset':Vector((0, -10))})
weight_toolbar.tool('Sample Vertex Group',   'sample_vertex_group', False, ToolIcon.PAINT_SAMPLE_VERTEX_GROUP, set(), {'offset':Vector((0, -10))})
weight_toolbar.tool('Select Box', 'select_box', False, ToolIcon.T_SELECT_BOX, {'ALWAYS_TRIGGER'}, {'operator':'bpy.ops.weightwheel.box_select_tool_options'})


class WEIGHT_OT_wheel(Operator):
    bl_idname = "weight.wheel"
    bl_label = "Weight Wheel"
    #bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'PAINT_WEIGHT'

    def finish(self, context):
        if hasattr(self, '_handler'):
            context.space_data.draw_handler_remove(self._handler, 'WINDOW')
            del self._handler
        context.tool_settings.weight_paint.show_brush = True
        Cursor.set_icon(context, CursorIcon.DEFAULT)

        for icon in self.tarta_icons:
            if icon:
                clear_image(icon)

        clear_image(self.none_icon[0])
        
        self.toolbar.unload()

    def init_weight(self):
        value = clamp(self.get_brush_weight(), 0, 1)
        #a = h - 1 if (h - 1) > 0 else h
        a = -value * 270-135

        self.color_handle_line = (
            get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.8, radians(a)),
            get_point_in_circle_from_angle(self.pos, self.color_ring_rad*1.03, radians(a))
        )

    def update_weight(self, mouse, context):

        direction = (mouse - self.pos).normalized()
        if direction == Vector((0, 0)):
            return

        if mouse[1] < self.pos[1]:
            angle = -direction.angle((self.pos.normalized()+Vector((114.5, 0.0))))
        else:
            angle = direction.angle((self.pos.normalized()+Vector((114.5, 0.0))))

        alpha = degrees(angle)

        # OLD !!!
        '''
        if alpha < 0:
            alpha += 360
        if (alpha < 225):
            value = 5/6*(1-alpha/225)
        elif (alpha > 315):
            value = 5/6+(1-((alpha-315)/45))/6
        '''
        # NEW !!!
        if alpha < 0 and mouse[0] < self.pos[0]:
            alpha += 360
        if (-45 < alpha < 225):
            value = 1 - (alpha+45)/270
        else:
            if (mouse[0] > self.pos[0]):
                value = 1
                angle = radians(-45)
            else:
                value = 0
                angle = radians(225)

        #print("Angle:", degrees(angle))
        #print("Factor:", degrees(angle)/360)
        #value = (degrees(angle)) / 360

        self.set_brush_weight(value, context)
        self.color_handle_line = (
            get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.8, angle),
            get_point_in_circle_from_angle(self.pos, self.color_ring_rad*1.03, angle)
        )
        #self.color = colorsys.hsv_to_rgb(h, s, v)

    def modal(self, context, event):
        context.area.tag_redraw()
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        if self.gestual:
            if event.type == 'LEFTMOUSE':
                if event.value == 'RELEASE':
                    self.gestual = False
                    self.gestual_sabe_dir = False
                    self.prev_brush_size = self.get_brush_size()
                    self.prev_brush_strength = self.get_brush_strength()
                    Cursor.set_icon(context, CursorIcon.PAINT_CROSS)
            elif event.type in {'RIGHTMOUSE', 'ESC'}:
                self.gestual = False
                self.gestual_sabe_dir = False
                Cursor.set_icon(context, CursorIcon.PAINT_CROSS)
                if self.invert_gestodir:
                    if self.gesto_dir == VERTICAL:
                        self.set_brush_strength(self.prev_brush_strength)
                    elif self.gesto_dir == HORIZONTAL:
                        self.set_brush_size(self.prev_brush_size)
                else:
                    if self.gesto_dir == VERTICAL: # or (self.gesto_dir == VERTICAL and self.invert_gestodir):
                        self.set_brush_size(self.prev_brush_size)
                    elif self.gesto_dir == HORIZONTAL:
                        self.set_brush_strength(self.prev_brush_strength)
            elif event.type == 'MOUSEMOVE':
                if self.gestual_sabe_dir:
                    self.update_gesto(mouse, event)
                else:
                    if abs(mouse[1] - self.prev_mouse[1]) > 6:
                        self.gesto_dir = VERTICAL
                        self.gestual_sabe_dir = True
                        self.prev_mouse = mouse
                    elif abs(mouse[0] - self.prev_mouse[0]) > 6:
                        self.gesto_dir = HORIZONTAL
                        self.gestual_sabe_dir = True
                        self.prev_mouse = mouse
            return {'RUNNING_MODAL'}
        elif self.coloring:
            if event.type == 'LEFTMOUSE':
                if event.value == 'RELEASE':
                    self.set_coloring(context, False)
            self.update_weight(mouse, context)
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC', 'WINDOW_DEACTIVATE'} or self.ctx_area != context.area:
            self.finish(context)
            return {'FINISHED'}
        elif event.type == self.key and event.value == 'RELEASE':
            if self.can_close:
                self.finish(context)
                return {'FINISHED'}
            else:
                self.can_close = True
            return {'RUNNING_MODAL'}
        elif self.toolbar.on_event(event, mouse):
            if self.draw_tool and self.draw_tool == self.toolbar.active_tool: # .on_hover(mouse, Vector((self.toolbar.item_size, self.toolbar.item_size))
                if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                    self.draw_tool_toggle = SUBSTRACT if self.draw_tool_toggle == ADD else ADD #ADD if mouse.y > self.draw_tool.center.y else SUBSTRACT
                    self.set_active_brush(context, 'Add' if self.draw_tool_toggle == ADD else 'Subtract')
            self.ctidx = -100
            self.ctrealidx = -100
            return {'RUNNING_MODAL'}
        elif self.wheel.show_markers and self.wheel.use_interactable_markers:
            self.on_hover_marker_button = None
            r = self.marker_button_rad
            for i, b in enumerate(self.marker_buttons):
                if point_inside_circle(mouse, b, r):
                    self.on_hover_marker_button = i
                    break
        return self.picker_mode(context, event, mouse)

    def picker_mode(self, context, event, mouse):
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.wheel.show_markers and self.wheel.use_interactable_markers and self.on_hover_marker_button is not None:
                    self.set_brush_weight(1-self.on_hover_marker_button/self.num_markers, context)
                    self.init_weight()
                    self.on_hover_marker_button = None
                    return {'RUNNING_MODAL'}
                elif point_inside_ring(mouse, self.pos, self.color_ring_rad*.85, self.color_ring_rad):
                    self.set_coloring(context, True)
                    return {'RUNNING_MODAL'}
                else:
                    if self.gestual_on_hover:# and self.active_tool_is_brush:
                        self.gestual = True
                        self.prev_mouse = mouse
                        Cursor.set_icon(context, CursorIcon.NONE)
                        return {'RUNNING_MODAL'}
                    elif self.ctidx != -100:
                        ######### self.wheel.call_custom_button(self.ctrealidx)# nope
                        self.ctidx = -100
                        self.tarta_piece_pressed = True
                        return {'RUNNING_MODAL'}
                
            elif event.value == 'RELEASE':
                if self.tarta_piece_pressed and self.ctrealidx != -100:
                    self.wheel.call_custom_button(self.ctrealidx)
                    self.ctrealidx = -100
                    self.tarta_piece_pressed = False
                    return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        else:
            if point_inside_circle(mouse, self.pos, self.gestual_pad_rad):
                self.gestual_on_hover = True
                self.ctidx = -100
                return {'RUNNING_MODAL'}
            self.gestual_on_hover = False
            if self.is_tarta_on_hover(context, mouse):
                return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}

    def get_active_tool(self, context):
        return context.tool_settings.weight_paint.brush
    
    def set_active_brush(self, context, brush_name):
        b = bpy.data.brushes.get(brush_name, None)
        if b:
            context.tool_settings.weight_paint.brush = b

    def invoke(self, context, event):
        active_tool = self.get_active_tool(context)
        if not active_tool:
            return {'FINISHED'}

        self.ups = context.tool_settings.unified_paint_settings
        self.active_tool = active_tool
        self.prev_brush_size = self.get_brush_size()
        self.prev_brush_strength = self.get_brush_strength()
        self.prev_brush_weight = self.get_brush_weight()

        self.prefs = get_prefs(context)
        self.wheel = context.scene.weight_wheel
        self.can_close = not self.prefs.keep_open
        self.theme = self.prefs.theme

        wheel_rad = self.rad = self.prefs.radius
        rel_rad_size = wheel_rad / 180
        win_h = context.window.height
        if win_h >= 1050 and win_h <= 1080:
            self.dpi_factor = 1.0
        else:
            self.dpi_factor = win_h / 1057 # 1057 without title bar of app.
            self.rad *= self.dpi_factor

        origin = Vector((event.mouse_region_x, event.mouse_region_y))

        self.color_ring_rad = int(self.rad * .73) #if self.wheel.show_markers else int(self.rad * .85)
        self.tarta_rad = int(self.color_ring_rad * .66)
        
        self.gestual_pad_rad = 40 if self.prefs.gesturepad_mode == 'SIMPLE' else 36
        self.gestual_pad_rad = max(24 * self.dpi_factor, self.gestual_pad_rad * self.dpi_factor * rel_rad_size)
        self.text_size = max(10, 12 * self.dpi_factor * rel_rad_size)

        # INIT VARS.
        kmi = context.window_manager.keyconfigs.user.keymaps['Weight Paint'].keymap_items.get('weight.wheel', None)
        self.key = kmi.type if kmi else 'SPACE'
        self.invert_gestodir = self.prefs.gesturepad_invert
        self.moving = False
        self.coloring = False
        self.color_handle_line = (Vector((0, 0)), Vector((0, 0)))

        # Gestual.
        self.prev_mouse = Vector((0, 0))
        self.gestual = False
        self.gestual_sabe_dir = False
        self.gestual_on_hover = False
        self.gesto_dir = NONE

        # Tarta.
        num_pieces = 0#len(self.wheel.custom_buttons)
        if num_pieces == 0:
            self.wheel.load_default_custom_buttons()
            num = 6
        else:
            num = min(10, max(4, num_pieces))
            num = num if num % 2 == 0 else num + 1
        num = 6
        self.ctnum = num
        self.ctidx = -100
        self.ctrealidx = -100
        self.tarta_piece_pressed = False
        self.tarta_icons = []
        self.none_icon = get_button_icon(ButtonIcon.NONE)

        for b in self.wheel.custom_buttons:
            ico = load_image_from_filepath(b.image_path)
            if ico:
                if not ico.name.startswith('.'):
                    ico.name = '.' + ico.name
                ico.gl_load()
                self.tarta_icons.append(ico)
            else:
                self.tarta_icons.append(None)

        self.tarta_pos = []
        self.tarta_item_rad = 30 if num == 4 else 26 if num == 6 else 22 if num == 8 else 16
        self.tarta_item_rad = max(12, self.tarta_item_rad*self.dpi_factor*rel_rad_size) # * self.dpi_factor, self.tarta_item_rad * self.dpi_factor) * 1.15
        angle_individual = radians(360 / num)
        half_num = (num / 2)
        init_angle = angle_individual * half_num
        half_angle_indiv = angle_individual / 2.0
        rad_tarta_items = self.tarta_rad - self.gestual_pad_rad + self.tarta_item_rad*.33
        point = Vector((origin.x + rad_tarta_items, origin.y))
        point = rotate_point_around_point(origin, point, init_angle - half_angle_indiv)
        self.tarta_pos.append(point)
        for i in range(0, num):
            point = rotate_point_around_point(origin, point, -angle_individual)
            self.tarta_pos.append(point)

        # Markers.
        if self.wheel.show_markers:
            self.marker_lines = []
            offset = origin
            radi = self.color_ring_rad * .98
            radf = self.color_ring_rad * 1.05
            num_markers = 10
            alpha = radians((360-90)/num_markers)
            point_norm = rotate_point_around_point(Vector((0, 0)), Vector((1, 0)), radians(-45))
            
            if self.wheel.use_interactable_markers:
                self.on_hover_marker_button = None
                self.marker_buttons = []
                radbut = radf * 1.1
                # Marker lines.
                for i in range(0, num_markers+1):
                    point_norm_transp = rotate_point_around_point(Vector((0, 0)), point_norm, alpha*i)
                    self.marker_lines.append(offset + point_norm_transp * radi)
                    self.marker_lines.append(offset + point_norm_transp * radf)
                
                    # Marker Buttons.
                    self.marker_buttons.append(offset + point_norm_transp * radbut)
                
                self.marker_button_rad = radbut - radf
            
            else:
                self.marker_labels = []
                radlbl = radf * 1.1
                
                for i in range(0, num_markers):
                    point_norm_transp = rotate_point_around_point(Vector((0, 0)), point_norm, alpha*i)
                    self.marker_lines.append(offset + point_norm_transp * radi)
                    self.marker_lines.append(offset + point_norm_transp * radf)
                    self.marker_labels.append(
                        (
                            offset + point_norm_transp * radlbl,
                            str(round(1-(i+1)/num_markers,2))
                        )
                    )
            self.num_markers = num_markers

        self.ctx_area = context.area
        self.pos = origin
        self.init_weight()
        
        self.toolbar = weight_toolbar
        self.toolbar.show(context, origin-Vector((0, self.color_ring_rad*.92)), 32*self.dpi_factor*rel_rad_size)
        
        if self.wheel.use_add_substract_brush:
            btype = active_tool.weight_tool
            self.draw_tool = self.toolbar.tools['Draw']
            if btype == 'DRAW' and active_tool.blend in {'ADD', 'SUB'}:
                self.draw_tool_toggle = ADD if active_tool.blend == 'ADD' else SUBSTRACT
            else:
                self.draw_tool_toggle = -1
            #self.draw_tool.label = active_tool.blend
        else:
            self.draw_tool = None
            self.draw_tool_toggle = -1

        if not context.window_manager.modal_handler_add(self):
            return {'CANCELLED'}
        context.tool_settings.weight_paint.show_brush = False
        self._handler = context.space_data.draw_handler_add(draw_callback_px, (self, context, origin), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def set_coloring(self, ctx, enable=False):
        self.coloring = enable
        #Cursor.set_icon(ctx, CursorIcon.NONE if enable else CursorIcon.PAINT_CROSS)

    def update_gesto(self, mouse, event):
        diff = mouse[self.gesto_dir] - self.prev_mouse[self.gesto_dir]
        if abs(diff) < 5:
            return

        if self.invert_gestodir:
            rate = 1 if not self.gesto_dir else .01
        else:
            rate = 1 if self.gesto_dir else .01
        if event.shift:
            rate *= .2
        elif event.ctrl:
            rate *= 2

        if self.invert_gestodir:
            if self.gesto_dir == VERTICAL:
                self.set_brush_strength(self.get_brush_strength() + rate * diff)
            elif self.gesto_dir == HORIZONTAL:
                self.set_brush_size(self.get_brush_size() + rate * diff)
        else:
            if self.gesto_dir == VERTICAL: # or (self.gesto_dir == VERTICAL and self.invert_gestodir):
                self.set_brush_size(self.get_brush_size() + rate * diff)
            elif self.gesto_dir == HORIZONTAL:
                self.set_brush_strength(self.get_brush_strength() + rate * diff)
        self.prev_mouse = mouse

    def get_brush_size(self):
        if not self.active_tool:
            return self.prev_brush_size
        if self.ups.use_unified_size:
            return self.ups.size
        return self.active_tool.size

    def get_brush_strength(self):
        if not self.active_tool:
            return self.prev_brush_strength
        if self.ups.use_unified_strength:
            return self.ups.strength
        return self.active_tool.strength

    def get_brush_weight(self):
        if self.ups.use_unified_weight:
            return self.ups.weight
        if not self.active_tool:
            return self.prev_brush_weight
        return self.active_tool.weight

    def set_brush_size(self, value):
        value = clamp(value, 1, 500)
        if self.ups.use_unified_size:
            self.ups.size = value
        else:
            self.active_tool.size = value

    def set_brush_strength(self, value):
        value = clamp(value, 0.01, 2)
        if self.ups.use_unified_strength:
            self.ups.strength = value
        else:
            self.active_tool.strength = value

    def set_brush_weight(self, value, context):
        value = clamp(value, 0, 1)
        if self.ups.use_unified_weight:
            self.ups.weight = value
        else:
            self.active_tool.weight = value
        if self.wheel.set_weight_of_selection_directly and self.use_selection_mask(context):
            bpy.ops.paint.weight_set()
            
    def use_selection_mask(self, context):
        data = context.active_object.data
        return data.use_paint_mask or data.use_paint_mask_vertex
    
    def active_tool_is_brush(self, context):
        return self.get_active_tool(context) and UnifiedPaintPanel.paint_settings(context)

    def is_tarta_on_hover(self, ctx, mouse):
        if point_inside_circle(mouse, self.pos, self.tarta_rad):
            v1 = direction_from_to(self.pos, mouse)
            v2 = direction_from_to(self.pos, self.pos+Vector((self.tarta_rad, 0)))
            angle = angle_between(v1, v2)
            single = 2*pi / self.ctnum
            half = floor(self.ctnum / 2.0) - 1
            self.ctidx = half - int(angle / single)
            if mouse[1] < self.pos[1]:
                self.ctrealidx = self.ctnum - self.ctidx - 1 # (self.ctnum - (half - self.ctidx) - 1)
                self.ctidx *= -1
                self.ctidx -= 1
            else:
                self.ctrealidx = self.ctidx

            if not self.active_tool_is_brush(ctx) and self.ctrealidx < 3:
                self.ctidx = -100
                self.ctrealidx = -100
                self.tarta_piece_pressed = False
                return False
            
            #print("%i - %f" % (self.ctrealidx, degrees(angle)))
            return True
        self.ctidx = -100
        self.ctrealidx = -100
        self.tarta_piece_pressed = False
        return False
