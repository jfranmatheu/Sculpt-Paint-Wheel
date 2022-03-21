from bpy.types import Operator, UILayout as UI, SpaceView3D
from bl_ui.properties_paint_common import UnifiedPaintPanel
from .. px.paint import *
from mathutils import Color, Vector
from math import cos, sin, tan, pi, degrees, atan, floor, log
from .. utils import * #Cursor, CursorIcon
from .. utils.checkers import is_gpencil, is_gpencil_paint
from .. addon import get_keyitem, get_prefs


class PAINT_OT_wheel(Operator):
    bl_idname = "paint.wheel"
    bl_label = "Paint Wheel"
    #bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_GPENCIL', 'VERTEX_GPENCIL'}

    def finish(self, context=None):
        if hasattr(self, '_handler'):
            SpaceView3D.draw_handler_remove(self._handler, 'WINDOW')
            del self._handler
        self.set_show_brush(context, True)
        Cursor.set_icon(context, CursorIcon.DEFAULT)
    
    def init_color(self):
        if not self.color:
            return
        r, g, b = self.color
        hsv = colorsys.rgb_to_hsv(r, g, b)
        h = hsv[0]
        a = h - 1 if (h - 1) > 0 else h
        a = (1 - a) * 360
        from math import radians
        self.handle_h = get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.92, radians(a))
        self.color_rect_bl = get_point_in_circle_from_angle(self.pos, self.color_rect_rad*1.425, PI_4)
        self.color_rect_tr = get_point_in_circle_from_angle(self.pos, self.color_rect_rad*1.425, PI5_4)
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

        if self.coloring_type == RING:
            direction = (mouse - self.pos).normalized()
            if direction == Vector((0, 0)):
                return

            if mouse[1] < self.pos[1]:
                ang = -direction.angle((self.pos.normalized()+Vector((114.5, 0.0)))) # pow(pi, pi+1)
            else:
                ang = direction.angle((self.pos.normalized()+Vector((114.5, 0.0)))) # pow(pi, pi+1)

            a = (degrees(ang)) / 360
            if a < 0:
                a += 1.0

            h = clamp(1-a, 0.0, 1.0)
            s = clamp(s, 0.0, 1.0)
            v = clamp(v, 0.0, 1.0)

            self.handle_h = get_point_in_circle_from_angle(self.pos, self.color_ring_rad*.92, ang)

        elif self.coloring_type == RECT:
            mx, my = (mouse - self.color_rect_tr) / self.color_rect_size[0]

            factor_inc_x = mx * cos(6.3 * mx) / 7 + 1.07
            factor_inc_y = my * cos(6.3 * my) / 7 + 1.07

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

            self.handle_sv = mouse
            self.clamp_color_handler()
        else:
            return

        self.color = colorsys.hsv_to_rgb(h, s, v)

    def modal(self, context, event):
        context.area.tag_redraw()
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        
        if self.coloring:
            if event.type == 'LEFTMOUSE':
                if event.value == 'RELEASE':
                    self.set_color(context)
                    self.set_coloring(context, False)
            self.update_color(mouse)
            return {'RUNNING_MODAL'}
        elif event.type == self.key and event.value == 'RELEASE':
            if self.can_close:
                self.finish(context)
                return {'FINISHED'}
            else:
                self.can_close = True
            return {'RUNNING_MODAL'}
        elif self.is_sliding_type:
            if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
                self.is_sliding_type = None
                return {'RUNNING_MODAL'}
            if self.is_sliding_type == SIZE:
                if mouse.x > self.pos.x:
                    size = 1
                    ang = 0
                elif mouse.y < self.pos.y:
                    size = 500
                    ang = radians(90)
                else:
                    # Calc.
                    first = self.pos + Vector((0, self.rad))
                    v1 = direction_from_to(self.pos, first)
                    v2 = direction_from_to(self.pos, mouse)
                    if v2 == Vector((0, 0)):
                        return {'RUNNING_MODAL'}
                    ang = angle_between(v1, v2)
                    factor = clamp(degrees(ang), 0, 90)/90
                    #print(factor)
                    if factor <= 0.5:
                        size = int(lerp(1, 100, factor*2))
                        if event.ctrl:
                            # s1: 108
                            # s2: 100
                            # s1 - s2 = 8 > 5
                            size_10units = int(size/10)*10
                            size = size_10units + 5 if size - size_10units > 4.9 else size_10units - 5
                            size = min(90, size)
                    else:
                        _size = lerp(100, 500, factor*2 - 1)
                        # ease_sine_in = -c * cos(t/d * (pi/2)) + c + b
                        size = int((ease_sine_in(factor*2 - 1, 100, 400) + _size) / 2)
                    #print(size)
                        if event.ctrl:
                            size_10units = int(size/10)*10
                            size = size_10units + 10 if size - size_10units > 10 else size_10units - 10
                            size = max(size, 100)
                # Set and update.
                self.set_brush_size(size)
                self.brush_size = self.get_brush_size()
                self.update_size_handler(ang)
            elif self.is_sliding_type == STRENGHT:
                if mouse.x < self.pos.x:
                    strenght = 2
                    ang = -radians(180)
                elif mouse.y > self.pos.y:
                    strenght = 0
                    ang = -radians(90)
                else:
                    # Calc.
                    first = self.pos + Vector((self.rad, 0))
                    v1 = direction_from_to(self.pos, first)
                    v2 = direction_from_to(self.pos, mouse)
                    if v2 == Vector((0, 0)):
                        return {'RUNNING_MODAL'}
                    _ang = angle_between(v1, v2)
                    ang = radians(90) - _ang - radians(180)
                    #print(degrees(_ang))
                    factor = clamp(degrees(_ang), 0, 90)/90.0
                    #print(factor)
                    strenght = factor*2.0
                    if event.ctrl:
                        strenght_1dec = round(strenght, 1)
                        strenght = strenght_1dec + .05 if strenght - strenght_1dec < 0.1 else strenght_1dec - .05
                # Set and update.
                self.set_brush_strength(strenght)
                self.brush_strength = self.get_brush_strength()
                self.update_strength_handler(ang)
            return {'RUNNING_MODAL'}
        elif not point_inside_circle(mouse, self.pos, self.color_ring_rad):
            if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
                #if context.mode == 'PAINT_TEXTURE':
                if point_inside_circle(mouse, self.handle_size, 10):
                    self.is_sliding_type = SIZE
                    return {'RUNNING_MODAL'}
                elif point_inside_circle(mouse, self.handle_strenght, 10):
                    self.is_sliding_type = STRENGHT
                    return {'RUNNING_MODAL'}
                #else:
                #    self.finish(context)
                #    return {'FINISHED'}
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC', 'WINDOW_DEACTIVATE'} or self.ctx_area != context.area:
            self.finish(context)
            return {'FINISHED'}
        return self.picker_mode(context, event, mouse)

    def picker_mode(self, context, event, mouse):
        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                if self.is_gpencil and not self.gpencil_use_color:
                    # Check for materials...
                    return {'RUNNING_MODAL'}
                if point_inside_rect(mouse, self.color_rect_tr, self.color_rect_size):
                    self.set_coloring(context, True, 1)
                    return {'RUNNING_MODAL'}
                elif point_inside_ring(mouse, self.pos, self.color_ring_rad*.85, self.color_ring_rad):
                    self.set_coloring(context, True, 0)
                    return {'RUNNING_MODAL'}
        return {'RUNNING_MODAL'}


    def invoke(self, context, event):
        if not UnifiedPaintPanel.paint_settings(context) and not is_gpencil(context):
            return {'FINISHED'}
        mode_settings = self.get_tool_settings(context)
        if not mode_settings:
            return {'FINISHED'}
        if not mode_settings.brush:
            return {'FINISHED'}

        self.is_gpencil = is_gpencil(context)
        if self.is_gpencil:
            if is_gpencil_paint(context):
                # Only vertex color, not material.
                self.gpencil_use_color = mode_settings.color_mode == 'VERTEXCOLOR' ## :-)))))))
            else:
                self.gpencil_use_color = True
        else:
            self.gpencil_use_color = False

        self.prefs = get_prefs(context)
        self.can_close = not self.prefs.keep_open
        self.theme = self.prefs.theme

        wheel_rad = self.rad = self.prefs.radius
        if not self.gpencil_use_color:
            wheel_rad = self.rad = 128
        win_h = context.window.height
        if win_h >= 1050 and win_h <= 1080:
            self.dpi_factor = 1.0
        else:
            self.dpi_factor = win_h / 1057 # 1057 without title bar of app.
            self.rad *= self.dpi_factor
        
        self.ups = context.tool_settings.unified_paint_settings if not self.is_gpencil else None
        self.active_tool = mode_settings.brush
        self.color = self.active_tool.color

        origin = Vector((event.mouse_region_x, event.mouse_region_y))

        self.color_ring_rad = self.rad * .85
        self.color_rect_rad = self.color_ring_rad * .55

        # INIT VARS.
        kmi = get_keyitem(context)
        self.key = kmi.type if kmi else 'SPACE'
        self.coloring = False
        self.coloring_type = -1
        self.handle_sv = Vector((0, 0))
        self.handle_h = Vector((0, 0))
        self.color_rect_bl = Vector((0, 0))
        self.color_rect_tr = Vector((0, 0))
        self.color_rect_size = Vector((0, 0))
        self.text_size = 12 * wheel_rad / 128 * self.dpi_factor

        self.ctx_area = context.area
        self.pos = origin
        self.init_color()
        
        #if context.mode == 'PAINT_TEXTURE':
        self.init_texture_paint(context)

        if not context.window_manager.modal_handler_add(self):
            return {'CANCELLED'}
        self.set_show_brush(context, False)
        self._handler = SpaceView3D.draw_handler_add(draw_callback_px, (self, context, origin), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}
    
    def init_texture_paint(self, context):
        self.is_sliding_type = None
        self.brush_size = self.get_brush_size()
        self.brush_strength = self.get_brush_strength()
        
        # Angulo / pos de los handlers de tamaño y fuerza de la brocha.
        self.update_size_handler()
        self.update_strength_handler()
        
    def evaluate_magic(self, t):
        return 602*t+103*t+1
        #print(self.inverse_evaluate_magic(self.brush_size/500))
        
    def evaluate_polinomial_magic(self, t):
        return (103 + sqrt(pow(103, 2) - 4*602 * (1 - t))) / (602 * 2)
    
    def evaluate_steps_magic(self, size):
        if size <= 100:
            return size/100/2.0
        else:
            #return smoothstep(101-500, 500, size) # -500 is a hack so is clamped between 0.5-1.0
            return lerp(0.5, 1.0, size/500)

    def update_size_handler(self, angle=-1):
        start = self.pos + Vector((0, self.rad)) 
        if angle == -1:
            factor = self.evaluate_steps_magic(self.brush_size)
            #print(factor)
            factor = clamp(factor, 0, 1)
            angle = factor*radians(90)
        self.handle_size = rotate_point_around_point(self.pos, start, angle)

    def update_strength_handler(self, angle=-1):
        start = self.pos + Vector((0, self.rad))
        if angle == -1:
            strength = self.brush_strength if self.brush_strength <= 2.0 else 2.0
            factor = strength/2.0
            factor = clamp(factor, 0, 1)
            #print(factor)
            angle = factor*radians(-90)-radians(90)
        self.handle_strenght = rotate_point_around_point(self.pos, start, angle)

    def get_tool_settings(self, ctx):
        if ctx.mode == 'PAINT_TEXTURE':
            return ctx.tool_settings.image_paint
        elif ctx.mode == 'PAINT_VERTEX':
            return ctx.tool_settings.vertex_paint
        elif ctx.mode == 'PAINT_GPENCIL':
            return ctx.tool_settings.gpencil_paint
        elif ctx.mode == 'VERTEX_GPENCIL':
            return ctx.tool_settings.gpencil_vertex_paint
        return None

    def set_show_brush(self, ctx, state):
        self.get_tool_settings(ctx).show_brush = state

    def set_color(self, ctx):
        self.get_tool_settings(ctx).brush.color = self.color

    def set_coloring(self, ctx, enable=False, _type=-1):
        self.coloring = enable
        self.coloring_type = _type
        Cursor.set_icon(ctx, CursorIcon.NONE if enable else CursorIcon.PAINT_CROSS)
        if enable:
            self.prev_color = self.active_tool.color.copy()
    
    def get_brush_size(self):
        #if not self.active_tool:
        #    return self.prev_brush_size
        if self.ups and self.ups.use_unified_size:
            return self.ups.size
        return self.active_tool.size

    def get_brush_strength(self):
        #if not self.active_tool:
        #    return self.prev_brush_strength
        if self.is_gpencil:
            return self.active_tool.gpencil_settings.pen_strength
        if self.ups and self.ups.use_unified_strength:
            return self.ups.strength
        return self.active_tool.strength

    def set_brush_size(self, value):
        value = clamp(value, 1, 500)
        if self.ups and self.ups.use_unified_size:
            self.ups.size = int(value)
        else:
            self.active_tool.size = int(value)

    def set_brush_strength(self, value):
        value = clamp(value, 0.01, 2)
        if self.is_gpencil:
            self.active_tool.gpencil_settings.pen_strength = value
        elif self.ups and self.ups.use_unified_strength:
            self.ups.strength = value
        else:
            self.active_tool.strength = value
