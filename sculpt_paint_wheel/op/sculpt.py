from bpy.types import Operator, UILayout as UI
from bl_ui.properties_paint_common import UnifiedPaintPanel
from .. px.sculpt import *
from mathutils import Color, Vector
from math import cos, sin, tan, pi, degrees, atan, floor, ceil
from .. gui_types.button import ButtonCircle
from .. data.icons import get_button_icon, ButtonIcon, get_tool_icon, DefToolImage
from .. utils import * #CursorIcon, Cursor, Anim, Ease, rotate_point_around_point, clear_image
from .. addon.prefs import get_prefs
from math import radians
from gpu.texture import from_image as gpu_texture_from_image
from sculpt_paint_wheel.props import Props

brush_idname_exceptions = {'MULTIPLANE_SCRAPE', 'TOPOLOGY'}

class SCULPT_OT_wheel(Operator):
    bl_idname = "sculpt.wheel"
    bl_label = "Sculpt Wheel"
    #bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'SCULPT'

    def finish(self, context):
        if hasattr(self, '_handler'):
            context.space_data.draw_handler_remove(self._handler, 'WINDOW')
            del self._handler
        context.tool_settings.sculpt.show_brush = True
        Cursor.set_icon(context, CursorIcon.DEFAULT)

        for icon in self.icons_others:
            if icon:
                clear_image(icon[0])
            # remove_image(icon)
        
        for icon in self.icons:
            if icon:
                clear_image(icon[0])
            # remove_image(icon)
        
        for icon in self.tarta_icons:
            if icon:
                clear_image(icon[0])
            # remove_image(icon)
        
        clear_image(self.none_icon[0])
    
    def init_color(self):
        if not self.color:
            return
        r, g, b = self.color
        hsv = colorsys.rgb_to_hsv(r, g, b)
        h = hsv[0]
        a = h - 1 if (h - 1) > 0 else h
        a = (1 - a) * 360
        
        self.handle_h = get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.92, radians(a))
        self.color_rect_bl = get_point_in_circle_from_angle(self.pos, self.color_rect_rad*1.5-3, PI_4)
        self.color_rect_tr = get_point_in_circle_from_angle(self.pos, self.color_rect_rad*1.5-3, PI5_4)
        self.color_rect_size = self.color_rect_bl - self.color_rect_tr
        x = hsv[1] * abs(self.color_rect_size[0])
        y = hsv[2] * abs(self.color_rect_size[1])
        self.handle_sv = Vector((x + self.color_rect_tr[0], y + self.color_rect_tr[1]))
        self.clamp_color_handler()

    def clamp_color_handler(self):
        if self.handle_sv[0] < self.color_rect_tr[0]:
            self.handle_sv[0] = self.color_rect_tr[0] + 1
        elif self.handle_sv[0] > self.color_rect_bl[0]:
            self.handle_sv[0] = self.color_rect_bl[0] - 1
        if self.handle_sv[1] < self.color_rect_tr[1]:
            self.handle_sv[1] = self.color_rect_tr[1] + 1
        elif self.handle_sv[1] > self.color_rect_bl[1]:
            self.handle_sv[1] = self.color_rect_bl[1] - 1

    def update_color(self, mouse):
        if not self.color:
            return

        r, g, b = self.color
        hsv = colorsys.rgb_to_hsv(r, g, b)
        h = float(hsv[0])
        s = float(hsv[1])
        v = float(hsv[2])
        #print("Init:", h)

        if self.coloring_type == RING:
            direction = (mouse - self.pos).normalized()
            if direction == Vector((0, 0)):
                return

            if mouse[1] < self.pos[1]:
                angle = -direction.angle((self.pos.normalized()+Vector((114.5, 0.0)))) # pow(pi, pi+1)
            else:
                angle = direction.angle((self.pos.normalized()+Vector((114.5, 0.0)))) # pow(pi, pi+1)

            #print("Angle:", degrees(angle))
            #print("Factor:", degrees(angle)/360)
            a = (degrees(angle)) / 360
            if a < 0:
                a += 1.0

            h = clamp(1-a, 0.0, 1.0)
            s = clamp(s, 0.0, 1.0)
            v = clamp(v, 0.0, 1.0)

            self.handle_h = get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.92, angle)

        elif self.coloring_type == RECT:
            mx, my = (mouse - self.color_rect_tr) / self.color_rect_size[0]

            factor_inc_x = mx * cos(6.3 * mx) / 7 + 1.07
            factor_inc_y = my * cos(6.3 * my) / 7 + 1.07
            # h = clamp(h, 0.0, 1.0)

            _s = pow(mx, factor_inc_x)
            if isinstance(_s, complex):
                s = 0.0
            else:
                s = clamp(_s, 0.0, 1.0)
            _v = pow(my, factor_inc_y)
            if isinstance(_v, complex):
                v = 0.0
            else:
                v = clamp(_v, 0.0, 1.0)

            #x = s * abs(size[0])
            #y = v * abs(size[1])
            self.handle_sv = mouse
            self.clamp_color_handler()
        else:
            return

        self.color = colorsys.hsv_to_rgb(h, s, v)
        #print("End:", h)

    def modal(self, context, event):
        #print(event.type)
        context.area.tag_redraw()
        if event.type == 'TIMER':
            if not self.animation:
                self.stop_anim_timer(context)
                return {'RUNNING_MODAL'}
            n = len(self.animation) - 1
            for i, anim in enumerate(reversed(self.animation)):
                if not anim():
                    a = self.animation.pop(n-i)
                    del a
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
                    if self.gesto_dir == VERTICAL:
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
                    context.tool_settings.sculpt.brush.color = self.color
                    self.set_coloring(context, False)
            # elif event.type == 'MOUSEMOVE':
            self.update_color(mouse)
            return {'RUNNING_MODAL'}
        elif self.moving:
            self.mouse_pos = mouse
            if event.type == 'LEFTMOUSE':
                if event.value == 'RELEASE':
                    if self.moving_remove:
                        #print("Moving:: Remove")
                        self.remove_tool(self.moving_tool_index)
                    #elif self.on_hover_between_tools_index != -1:
                    #    self.rearrange_tools(context, self.moving_tool_index, self.on_hover_between_tools_index)
                    else:
                        #print("Moving:: Swap")
                        self.swap_tools(context, self.moving_tool_index, self.on_hover_tool_index)
                    self.moving_tool_index = -1
                    self.moving = False
            #elif self.check_on_hover_in_between(mouse):
            #    pass
            elif not self.check_on_hover_tool(mouse):
                self.moving_remove = not point_inside_circle(mouse, self.pos, self.rad + self.tool_rad)
            else:
                self.moving_remove = False
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC', 'WINDOW_DEACTIVATE'} or self.ctx_area != context.area:
            self.finish(context)
            return {'FINISHED'}
        elif event.type == self.key and event.value == 'RELEASE':
            if self.prefs.on_release_select:
                if self.check_on_hover_tool(mouse):
                    self.active_toolset.select_tool(context, self.on_hover_tool_index)
                    self.finish(context)
                    return {'FINISHED'}
            if self.can_close:
                self.finish(context)
                return {'FINISHED'}
            else:
                self.can_close = True
            return {'RUNNING_MODAL'}
        elif not point_inside_circle(mouse, self.pos, self.rad):
            self.on_hover_tool_index = -1
            self.on_hover_tool_pos = None
            self.ctidx = -100
            self.tarta_piece_pressed = False
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                if self.active_button:
                    self.active_button(context)
                elif self.on_hover_toolset_pos:
                    # self.active_toolset_index = self.on_hover_toolset_index
                    self.wheel.active_toolset = self.on_hover_toolset_index
                    self.finish(context)
                    off = Vector((context.region.x, context.region.y))
                    Cursor.set_icon(context, CursorIcon.NONE)
                    Cursor.wrap(*(self.pos+off), context)
                    bpy.ops.sculpt.wheel('INVOKE_DEFAULT')
                    Cursor.wrap(*(mouse+off), context)
                    Cursor.set_icon(context, CursorIcon.PAINT_CROSS)
                    return {'FINISHED'}
                else:
                    self.finish(context)
                    return {'FINISHED'}
            for b in self.outsider_buttons:
                if b.check(mouse):
                    self.active_button = b
                    return {'RUNNING_MODAL'}
            self.active_button = None
            if self.mode == 'PICKER':
                for i, ts in enumerate(self.toolset_pos):
                    if point_inside_circle(mouse, ts, self.toolset_rad+3):
                        self.on_hover_toolset_pos = ts
                        self.on_hover_toolset_index = i
                        return {'RUNNING_MODAL'}
            self.on_hover_toolset_pos = None
            self.on_hover_toolset_index = -1
            return {'RUNNING_MODAL'}
        elif self.mode == 'PICKER':
            return self.picker_mode(context, event, mouse)
        elif self.mode == 'EDIT':
            return self.edit_mode(context, event, mouse)
        return {'RUNNING_MODAL'}

    def picker_mode(self, context, event, mouse):
        self.on_hover_toolset_pos = None
        self.on_hover_toolset_index = -1
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.color:
                    if point_inside_rect(mouse, self.color_rect_tr, self.color_rect_size):
                        self.set_coloring(context, True, 1)
                        return {'RUNNING_MODAL'}
                    elif point_inside_ring(mouse, self.pos, self.color_ring_rad*.85, self.color_ring_rad):
                        self.set_coloring(context, True, 0)
                        return {'RUNNING_MODAL'}
                else:
                    if self.gestual_on_hover and self.active_tool_is_brush:
                        self.gestual = True
                        self.prev_mouse = mouse
                        Cursor.set_icon(context, CursorIcon.NONE)
                        return {'RUNNING_MODAL'}
                    elif self.ctidx != -100:
                        # self.wheel.call_custom_button(self.ctrealidx)
                        self.ctidx = -100
                        self.tarta_piece_pressed = True
                        return {'RUNNING_MODAL'}
                if self.on_hover_tool_pos:
                    if self.active_tool_pos != self.on_hover_tool_pos and self.active_toolset.check_tool(self.on_hover_tool_index):
                        #print("PICKED TOOL:", self.on_hover_tool_index)
                        self.active_tool_pos = self.on_hover_tool_pos
                        self.active_toolset.select_tool(context, self.on_hover_tool_index)
                        active_tool = context.tool_settings.sculpt.brush
                        if not active_tool or not UnifiedPaintPanel.paint_settings(context):
                            self.color = None
                            self.active_tool_is_brush = False
                            self.active_tool_index = self.on_hover_tool_index
                            return {'RUNNING_MODAL'}
                        elif active_tool.sculpt_tool in {'PAINT', 'SMEAR'}:
                            self.color = active_tool.color
                            self.init_color()
                            self.active_tool_is_brush = True
                        # NOTE: CO/UNCOMMENT THIS.
                        else:
                            self.color = None
                            self.active_tool_is_brush = True
                        self.active_tool = active_tool
                        self.active_tool_index = self.on_hover_tool_index
                        self.prev_brush_size = self.get_brush_size()
                        self.prev_brush_strength = self.get_brush_strength()
                    return {'RUNNING_MODAL'}
                    #self.finish(context)
                    #return {'FINISHED'}
            elif event.value == 'RELEASE':
                if self.tarta_piece_pressed and self.ctrealidx != -100:
                    self.wheel.call_custom_button(self.ctrealidx)
                    self.ctrealidx = -100
                    self.tarta_piece_pressed = False
                    return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            if self.on_hover_tool_index != -1:
                self.active_toolset.show_tool_context_menu(self.on_hover_tool_index)
                return {'RUNNING_MODAL'}
            return {'RUNNING_MODAL'}
        else:
            for i, tool_pos in enumerate(self.tool_pos):
                if point_inside_circle(mouse, tool_pos, self.tool_rad):
                    self.on_hover_tool_pos = tool_pos
                    self.on_hover_tool_index = i
                    self.ctidx = -100
                    self.gestual_on_hover = False
                    return {'RUNNING_MODAL'}
            self.on_hover_tool_index = -1
            self.on_hover_tool_pos = None
            if point_inside_circle(mouse, self.pos, self.gestual_pad_rad):
                self.gestual_on_hover = True
                self.ctidx = -100
                return {'RUNNING_MODAL'}
            self.gestual_on_hover = False
            if self.is_tarta_on_hover(mouse):
                return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}

    def edit_mode(self, context, event, mouse):
        # if self.color:
        for i, tool_pos in enumerate(self.tool_pos):
            if point_inside_circle(mouse, tool_pos, self.tool_rad):
                self.on_hover_tool_pos = tool_pos
                self.on_hover_tool_index = i
                if event.type == 'LEFTMOUSE':
                    if event.value == 'PRESS':
                        self.mouse_pos = mouse
                        self.moving = True
                        self.moving_tool_index = i
                return {'RUNNING_MODAL'}
        self.on_hover_tool_index = -1
        self.on_hover_tool_pos = None
        if point_inside_circle(mouse, self.pos, self.gestual_pad_rad):
            self.ctidx = -100
            return {'RUNNING_MODAL'}
        if self.is_tarta_on_hover(mouse):
            return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}

    def check_on_hover_tool(self, mouse):
        for i, tool_pos in enumerate(self.tool_pos):
            if point_inside_circle(mouse, tool_pos, self.tool_rad):
                self.on_hover_tool_pos = tool_pos
                self.on_hover_tool_index = i
                return True
        self.on_hover_tool_index = -1
        self.on_hover_tool_pos = None
        return False

    def check_on_hover_in_between(self, mouse):
        for i, sep in enumerate(self.slots_between_tools):
            if point_inside_circle(mouse, sep, 8):
                self.on_hover_between_tools_index = i
                return True
        self.on_hover_between_tools_index = -1
        return False

    def invoke(self, context, event):
        sculpt_wheel = Props.SculptWheelData(context)
        self.active_tool_pos = None
        self.on_hover_tool_index = -1
        active_tool = context.tool_settings.sculpt.brush
        if not active_tool:
            return {'FINISHED'}
        b_type = active_tool.sculpt_tool
        self.ups = context.tool_settings.unified_paint_settings
        if not b_type in brush_idname_exceptions:
            b_type = active_tool.sculpt_tool.replace('_', ' ').title()
            idname = context.workspace.tools.from_space_view3d_mode('SCULPT').idname
            t_type = idname.split('.')[1]
            if b_type != t_type:
                active_tool = idname
                self.active_tool = None
                self.prev_brush_size = 0
                self.prev_brush_strength = 0
            else:
                self.active_tool = active_tool
                self.prev_brush_size = self.get_brush_size()
                self.prev_brush_strength = self.get_brush_strength()
        else:
            self.active_tool = active_tool
            self.prev_brush_size = self.get_brush_size()
            self.prev_brush_strength = self.get_brush_strength()

        self.prefs = get_prefs(context)
        self.wheel = sculpt_wheel
        self.can_close = not self.prefs.keep_open
        self.active_toolset = self.wheel.get_active_toolset()
        self.theme = self.prefs.theme

        # Load toolsets.
        if not self.active_toolset:
            bpy.ops.sculpt.wheel_init_toolsets()
            self.active_toolset = self.wheel.get_active_toolset()
            if not self.active_toolset:
                return {'CANCELLED'}

        wheel_rad = self.rad = self.prefs.radius
        win_h = context.window.height
        if win_h >= 1050 and win_h <= 1080:
            self.dpi_factor = 1.0
        else:
            self.dpi_factor = win_h / 1057 # 1057 without title bar of app.
            self.rad *= self.dpi_factor


        # Purge possible invalid tools:
        invalid_tools = []
        for idx, t in enumerate(self.active_toolset.tools):
            if t.idname:
                continue
            if t.tool is None:
                invalid_tools.append(idx)
        for tool in invalid_tools:
            self.active_toolset.remove_tool(tool)


        self.num_tools = max(7, len(self.active_toolset.tools))
        self.use_two_tool_circles = self.num_tools > 16
        self.tool_padding = 20 * self.dpi_factor
        self.num_tools_inner = 0
        off_outter = self.tool_padding * self.num_tools * self.rad / 180
        off_inner = 0

        if not UnifiedPaintPanel.paint_settings(context):
            self.color = None
            self.active_tool_is_brush = False
        else:
            if isinstance(active_tool, str):
                active_tool = context.tool_settings.sculpt.brush
            if active_tool.sculpt_tool not in {'PAINT', 'SMEAR'}:
                self.color = None
                self.active_tool_is_brush = True
            else:
                self.color = active_tool.color
                self.active_tool_is_brush = True

        origin = Vector((event.mouse_region_x, event.mouse_region_y))

        

        if self.use_two_tool_circles:
            self.rad *= 1.2
            self.toolcircle_outer_rad = self.rad * .935
            tool_circle_counts = (
                ceil(self.num_tools * .6), # outer
                ceil(self.num_tools * .4)  # inner
            )
            diff_count = self.num_tools - (tool_circle_counts[0] + tool_circle_counts[1])
            if diff_count != 0:
                tool_circle_counts = (
                    tool_circle_counts[0],
                    tool_circle_counts[1] + diff_count
                )
            self.tool_rad = getr_big_small_circles_3(self.toolcircle_outer_rad, self.num_tools) * 1.5
            self.tool_rad = clamp(self.tool_rad, 24, 30) if self.rad < 400 else self.tool_rad * .8
            toolcircle_rad = self.toolcircle_outer_rad - self.tool_rad
            self.toolcircle_rad = tool_circle_rads = (
                toolcircle_rad,
                toolcircle_rad - self.tool_rad * 2.0
            )
            self.tool_circle_counts = tool_circle_counts
            self.toolcircle_inner_rad = self.toolcircle_outer_rad - self.tool_rad * 2.0 * 2.0 * .95
        else:
            self.toolcircle_outer_rad = self.rad * .925
            self.tool_rad = getr_big_small_circles_3(self.toolcircle_outer_rad, self.num_tools)
            self.tool_rad = clamp(self.tool_rad, 24, 32) if self.rad < 200 else self.tool_rad * .8
            #self.tool_rad *= self.prefs.tool_icon_scale
            self.toolcircle_rad = self.toolcircle_outer_rad - self.tool_rad
            self.toolcircle_inner_rad = self.toolcircle_outer_rad - self.tool_rad * 2.0

        self.tool_pos = []
        if self.use_two_tool_circles:

            #half_num_tools = ceil(self.num_tools * .5)
            #angle = radians(360 / half_num_tools)
            for i in range(2):
                prev_angle = 0
                tool_count = tool_circle_counts[i]
                angle = radians(360 / tool_count)
                tool_rad = tool_circle_rads[i]
                point = Vector((origin.x, origin.y + tool_rad))
                if i != 0:
                    point = rotate_point_around_point(origin, point, -prev_angle/2 * i)
                self.tool_pos.append(point)
                for i in range(1, tool_count):
                    point = rotate_point_around_point(origin, point, -angle)
                    self.tool_pos.append(point)
                prev_angle = angle
        else:
            angle = radians(360 / self.num_tools)
            point = Vector((origin.x, origin.y + self.toolcircle_rad))
            self.tool_pos.append(point)
            #tick = True
            #f_rad = self.tool_rad * .25
            for i in range(1, self.num_tools):
                point = rotate_point_around_point(origin, point, -angle)
                #if tick:
                #    self.tool_pos.append(point - direction_from_to(point, origin) * f_rad)
                #else:
                self.tool_pos.append(point)
                #tick = not tick

        
        self.color_ring_rad = self.toolcircle_inner_rad * .85
        self.color_rect_rad = self.color_ring_rad * .55
        self.tarta_rad = self.color_ring_rad * .7

        if wheel_rad > 150 and wheel_rad < 200 and self.dpi_factor < 1.05 and self.dpi_factor > .95:
            self.gestual_pad_rad = 36 if self.prefs.gesturepad_mode == 'SIMPLE' else 32 # self.color_rect_rad # min(36, self.color_ring_rad * .45)
            self.text_size = 12
        else:
            if wheel_rad < 150:
                self.gestual_pad_rad = int(self.tarta_rad * .7)
                self.text_size = 12 * wheel_rad / 128 * self.dpi_factor
            else:
                self.gestual_pad_rad = int(self.tarta_rad * .6)
                self.text_size = 12 * wheel_rad / 150 * self.dpi_factor


        self.icons = []
        from bpy.path import abspath as b3d_abspath
        for i, t in enumerate(self.active_toolset.tools):
            if t:
                if t.tool is None:
                    continue
                if t.idname:
                    if t.idname == active_tool:
                        self.active_tool_pos = self.tool_pos[i]
                        self.active_tool_index = i
                    ico = get_tool_icon(t.idname, False)
                else:
                    if t.tool == active_tool:
                        self.active_tool_pos = self.tool_pos[i]
                        self.active_tool_index = i
                    if t.tool.use_custom_icon:
                        icopath = t.tool.icon_filepath if not t.tool.icon_filepath.startswith('//') else b3d_abspath(t.tool.icon_filepath, library=t.tool.library)
                        ico = load_image_from_filepath(icopath)
                    else:
                        ico = get_tool_icon(t.tool)
                if not ico:
                    ico = DefToolImage.DEFAULT()
                if not ico.name.startswith('.'):
                    ico.name = '.' + ico.name

                self.icons.append((ico, gpu_texture_from_image(ico)))

        self.toolset_pos = []
        self.toolset_rad = 6 * wheel_rad / 180 * self.dpi_factor
        # self.toolset_rad = 6 * self.dpi_factor
        self.active_toolset_index = self.wheel.active_toolset
        angle = radians(-8)
        point = Vector((origin.x, origin.y + self.rad + self.toolset_rad * 2))
        point = rotate_point_around_point(origin, point, radians(45))
        self.toolset_pos.append(point)
        for i in range(1, len(self.wheel.toolsets)):
            point = rotate_point_around_point(origin, point, angle)
            self.toolset_pos.append(point)

        # INIT VARS.
        # kmi = context.window_manager.keyconfigs.addon.keymaps['Sculpt'].keymap_items.get('sculpt.wheel', None)
        kmi = context.window_manager.keyconfigs.user.keymaps['Sculpt'].keymap_items.get('sculpt.wheel', None)
        self.key = kmi.type if kmi else 'SPACE'
        self.mode = 'PICKER'
        self.invert_gestodir = self.prefs.gesturepad_invert
        self.moving = False
        self.moving_remove = False
        self.moving_tool_index = -1
        self.on_hover_tool_pos = None
        self.on_hover_toolset_pos = None
        self.coloring = False
        self.coloring_type = -1
        self.handle_sv = Vector((0, 0))
        self.handle_h = Vector((0, 0))
        self.color_rect_bl = Vector((0, 0))
        self.color_rect_tr = Vector((0, 0))
        self.color_rect_size = Vector((0, 0))
        self.outsider_buttons = []
        self.animation = []
        # Gestual.
        self.prev_mouse = Vector((0, 0))
        self.gestual = False
        self.gestual_sabe_dir = False
        self.gestual_on_hover = False
        self.gesto_dir = NONE
        # self.active_tool = active_tool
        if not hasattr(self, 'active_tool_index'):
            self.active_tool_index = -1

        # Tarta.
        num_pieces = len(self.wheel.custom_buttons)
        if num_pieces == 0:
            self.wheel.load_custom_buttons(context)
            num = len(self.wheel.custom_buttons)
        else:
            num = min(10, max(4, num_pieces))
            num = num if num % 2 == 0 else num + 1
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
                self.tarta_icons.append((ico, gpu_texture_from_image(ico)))
            else:
                self.tarta_icons.append(None)
        self.tarta_pos = []
        if wheel_rad < 150 or  wheel_rad > 240:
            self.tarta_rad += 3
            self.tarta_item_rad = 16 * self.rad / 128
        else:
            self.tarta_item_rad = 30 if num == 4 else 26 if num == 6 else 22 if num == 8 else 16
            self.tarta_item_rad *= self.dpi_factor
        angle_individual = radians(360 / num)
        half_num = (num / 2)
        init_angle = angle_individual * half_num
        half_angle_indiv = angle_individual / 2.0
        point = Vector((origin.x + self.tarta_rad, origin.y))
        point = rotate_point_around_point(origin, point, init_angle - half_angle_indiv)
        self.tarta_pos.append(point)
        for i in range(0, num):
            point = rotate_point_around_point(origin, point, -angle_individual)
            self.tarta_pos.append(point)

        # Button: Toggle Mode.
        self.icons_others = []
        ico, gpu_texture = get_button_icon(ButtonIcon.EDIT)
        self.icons_others.append((ico, gpu_texture_from_image(ico)))
        rad = 16 * wheel_rad / 180 * self.dpi_factor
        left = origin - Vector((self.rad + rad * 2 + 10, 0))
        pos = rotate_point_around_point(origin, left, radians(45))
        but_mode_toggle = ButtonCircle(pos, rad, (.9, .9, .9, .65), gpu_texture, self.toggle_mode)
        self.outsider_buttons.append(but_mode_toggle)

        self.ctx_area = context.area
        self.pos = origin
        self.init_color()
        #self.init_slots_between_tools()
        if not context.window_manager.modal_handler_add(self):
            return {'CANCELLED'}
        context.tool_settings.sculpt.show_brush = False
        self._handler = context.space_data.draw_handler_add(draw_callback_px, (self, context, origin), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def toggle_mode(self):
        self.mode = 'EDIT' if self.mode == 'PICKER' else 'PICKER'

    def init_slots_between_tools(self):
        self.on_hover_between_tools_index = -1
        if hasattr(self, 'slots_between_tools'):
            self.slots_between_tools.clear()
        else:
            self.slots_between_tools = []
        p = self.tool_pos[-1]
        for t in self.tool_pos:
            self.slots_between_tools.append((p + t) / 2.0)
            p = t

    def set_coloring(self, ctx, enable=False, _type=-1):
        self.coloring = enable
        self.coloring_type = _type
        Cursor.set_icon(ctx, CursorIcon.NONE if enable else CursorIcon.PAINT_CROSS)

    def swap_tools(self, context, tool_1, tool_2):
        n = len(self.active_toolset.tools) - 1
        if tool_1 == tool_2 or tool_1 < 0 or tool_2 < 0 or tool_1 > n or tool_2 > n:
            return
        # NOPE, DON'T DO THAT LOL.
        # self.tool_pos[tool_1], self.tool_pos[tool_2] = self.tool_pos[tool_2], self.tool_pos[tool_1]
        if self.tool_pos[tool_1] == self.active_tool_pos:
            self.active_tool_pos = self.tool_pos[tool_2]
            self.active_tool_index = tool_2
        elif self.tool_pos[tool_2] == self.active_tool_pos:
            self.active_tool_pos = self.tool_pos[tool_1]
            self.active_tool_index = tool_1
        # self.icons[tool_1], self.icons[tool_2] = self.icons[tool_2], self.icons[tool_1]
        temp = self.tool_pos[tool_1]
        kwargs = {
            'tool_1' : tool_1,
            'tool_2' : tool_2
        }
        if self.add_animation(context, "tool_pos#"+str(tool_2), temp, 0.2, self.swap_back_tools, None, **kwargs):
            self.tool_pos[tool_1] = self.tool_pos[tool_2]
        else:
            self.icons[tool_1], self.icons[tool_2] = self.icons[tool_2], self.icons[tool_1]
        self.active_toolset.swap_tools(tool_1, tool_2)

    def swap_back_tools(self, **kwargs):
        tool_1 = kwargs['tool_1']
        tool_2 = kwargs['tool_2']
        # self.debug_tool(tool_1)
        # self.debug_tool(tool_2)
        temp = self.tool_pos[tool_1] * 1
        self.tool_pos[tool_1] = self.tool_pos[tool_2]
        self.tool_pos[tool_2] = temp
        self.icons[tool_1], self.icons[tool_2] = self.icons[tool_2], self.icons[tool_1]
        # self.debug_tool(tool_1)
        # self.debug_tool(tool_2)

    def rearrange_tools(self, context, moving_tool, in_between_slot):
        #print("Moving Index:", moving_tool)
        #print("In between Slot:", in_between_slot)
        prev_tool = in_between_slot - 1 if in_between_slot > 0 else self.num_tools - 1
        next_tool = in_between_slot + 1 if in_between_slot < self.num_tools - 1 else 0
        sign = distance_between(self.mouse_pos, self.tool_pos[prev_tool]) < distance_between(self.mouse_pos, self.tool_pos[next_tool])
        target_tool_idx = in_between_slot - int(sign)
        if target_tool_idx < 0:
            target_tool_idx = self.num_tools - 1
        elif target_tool_idx >= self.num_tools:
            target_tool_idx = 0
        #print("Target Index:", target_tool_idx)
        #if moving_tool < target_tool_idx:
        #    lower = moving_tool
        #    greater = target_tool_idx
        #else:
        #    lower = target_tool_idx
        #    greater = moving_tool
        #tramo_1 = list(range(0, lower)) # self.tool_pos[:lower-1]
        #tramo_2 = list(range(lower, greater)) # self.tool_pos[lower:greater]
        #tramo_3 = list(range(greater, self.num_tools)) # self.tool_pos[greater:]

        # 1. Mover tool al slot target calculado.
        self.add_animation(context, "tool_pos#"+str(moving_tool), self.tool_pos[target_tool_idx], 0.16)
        # self.icons[moving_tool], self.icons[target_tool_idx] = self.icons[target_tool_idx], self.icons[moving_tool]
        # self.swap_tools(context, moving_tool, target_tool_idx)

        # 2. Ir en la dirección hacia donde colocaste para
        # ir moviendo la siguiente tool hasta el siguiente slot...
        # así hasta llegar al slot de moving tool.
        dir = -1 if sign else 1 # NOTE: maybe inverted.
        current_index = target_tool_idx - dir
        while current_index != moving_tool:
            current_index += dir
            if current_index < 0:
                current_index = self.num_tools - 1
            elif current_index >= self.num_tools:
                current_index = 0
            next_dir = current_index + dir
            if next_dir < 0:
                next_dir = self.num_tools - 1
            elif next_dir >= self.num_tools:
                next_dir = 0
            #print(current_index, "- to -", next_dir)
            self.add_animation(context, "tool_pos#"+str(current_index), self.tool_pos[next_dir], 0.16)
            #self.icons[current_index], self.icons[next_dir] = self.icons[next_dir], self.icons[current_index]

    def remove_tool(self, tool):
        if tool == -1:
            return
        self.tool_pos.pop(tool)
        self.icons.pop(tool)
        self.active_toolset.remove_tool(tool)

    def start_anim_timer(self, context):
        if not hasattr(self, 'anim_timer'):
            self.anim_timer = context.window_manager.event_timer_add(0.04, window=context.window)

    def stop_anim_timer(self, context):
        if hasattr(self, 'anim_timer'):
            context.window_manager.event_timer_remove(self.anim_timer)
            del self.anim_timer

    def add_animation(self, context, attr: str, dest, time: float, on_end=None, *end_args, **end_kwargs):
        anim = Anim(self, attr, dest, time)
        if anim:
            self.animation.append(anim)
            self.start_anim_timer(context)
            if on_end:
                #print(end_args)
                #print(end_kwargs)
                anim.set_on_end(on_end, *end_args if end_args else None, **end_kwargs if end_kwargs else None)
            return True
        else:
            return False

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
            if self.gesto_dir == VERTICAL:# or (self.gesto_dir == VERTICAL and self.invert_gestodir):
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

    def set_brush_size(self, value):
        value = clamp(value, 1, 500)
        if self.ups.use_unified_size:
            self.ups.size = int(value)
        else:
            self.active_tool.size = int(value)

    def set_brush_strength(self, value):
        value = clamp(value, 0.01, 2)
        if self.ups.use_unified_strength:
            self.ups.strength = value
        else:
            self.active_tool.strength = value

    def is_tarta_on_hover(self, mouse):
        if point_inside_circle(mouse, self.pos, self.color_ring_rad):
            v1 = direction_from_to(self.pos, mouse)
            v2 = direction_from_to(self.pos, self.pos+Vector((self.color_ring_rad, 0)))
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
            #print("%i - %f" % (self.ctrealidx, degrees(angle)))
            return True
        self.ctidx = -100
        self.ctrealidx = -100
        self.tarta_piece_pressed = False
        return False

    def debug_tool(self, index):
        print("TOOL AT INDEX %i :" % index)
        print("\t- Name: ", self.active_toolset.tools[index].name)
        print("\t- Position: ", self.tool_pos[index])
        print("\t- Icon: ", self.icons[index])
