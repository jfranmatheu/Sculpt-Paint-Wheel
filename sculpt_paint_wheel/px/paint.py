import bpy
from .. gpu.dibuix import *
import colorsys
from .. utils.fun import smoothstep, rotate_point_around_point, direction_from_to
from math import pi, radians
from mathutils import Vector
from .. gpu.text import Draw_Text, Draw_Text_AlignCenter, Draw_Text_Right, SetFontSize, GetFontDim

from .. gpu.gl_fun import SetLineSBlend as _SetLineSBlend, RstLineSBlend as _RstLineSBlend

PI_4 = pi / 4
PI5_4 = 5 * pi / 4
RING = 0
RECT = 1
SIZE = 2
STRENGHT = 3
HORIZONTAL = 0
VERTICAL = 1
NONE = -1


def draw_callback_px(op, ctx, o):
    if ctx.area != op.ctx_area:
        return

    if op.is_gpencil:
        DiCFS(o, op.rad*1.32, (.05, .05, .05, .75))
    DiCFS(o, op.rad, op.theme.base_color)
    DiRNGBLR(o, op.rad*.95, .02, .01, (.05, .05, .05, .95))
    #DiCLS(o, op.rad*.95, 64, 1.5, (.4, .4, .4, .9))
    ts_12 = int(op.text_size)
    ts_10 = int(ts_12 * 10/12)
    ts_16 = int(ts_12 * 16/12)
    ts_13 = int(ts_12 * 13/12)
    dpi = op.dpi_factor

    SetBlend()
    if not op.is_sliding_type:
        #RstColorSpace()
        c = colorsys.rgb_to_hsv(*op.color)
        sv = (1.0, 1.0) if op.prefs.color_picker.lock_ring_sv else (float(c[1]), float(c[2]))
        DiANILLOTONO(o, op.color_ring_rad, *sv)
        DiPKCO(o, op.color_rect_rad, float(c[0]))
        _SetLineSBlend(1.5)
        DiCLS(op.handle_h, 3*dpi, 12, 1.3, (1, 1, 1, 1))
        DiCLS(op.handle_h, 4*dpi, 12, 1.3, (0, 0, 0, 1))
        DiCLS(op.handle_sv, 3*dpi, 12, 1.3, (1, 1, 1, 1))
        DiCLS(op.handle_sv, 4*dpi, 12, 1.3, (0, 0, 0, 1))
        _RstLineSBlend()
        '''
        if op.coloring:
            v = smoothstep(0, 1, 1 - c[2])
            if op.coloring_type == RING:
                rgb = op.color if not op.prefs.color_picker.lock_ring_sv else (1.0,1.0,1.0)
                DiCFCL(op.handle_h, 9*dpi if not op.prefs.color_picker.lock_ring_sv else 4.5*dpi, [*rgb, 1], (v, v, v, 1))
            elif op.coloring_type == RECT:
                DiCFCL(op.handle_sv, 9*dpi, [*op.color, 1], (v, v, v, 1))
        '''
        #SetSRGB()
        # Tapar/overlay para desactivar el pk.
        if op.is_gpencil and not op.gpencil_use_color:
            DiCFS(o, op.color_ring_rad+5, (.1, .1, .1, .8))
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*.15, "Not available in", ts_13, (.92, .92, .92, .66))
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*-.15, "Material Paint Mode", ts_13, (.92, .92, .92, .66))
            
    else:
        if op.is_sliding_type == SIZE:
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*.3, "Size", ts_16)
            Draw_Text_AlignCenter(o[0], o[1]-op.rad*.3, str(op.brush_size), ts_16)
            _SetLineSBlend(1.5)
            DiCLS(o, 100, 32, 1.5, (.8, .8, .8, .5))
            DiCLS(o, op.brush_size, 64 if op.brush_size > 100 else 36 if op.brush_size > 40 else 16, 1.5, (1, 1, 0, 1))
            _RstLineSBlend()
        elif op.is_sliding_type == STRENGHT:
            rad095 = op.rad*.95
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*.3, "Strength", ts_16)
            Draw_Text_AlignCenter(o[0], o[1]-op.rad*.3, str(round(op.brush_strength,2)), ts_16)
            _SetLineSBlend(1.5)
            DiCLS(o, rad095*.5, 32, 1.5, (.8, .8, .8, .5))
            DiCLS(o, rad095*(op.brush_strength/2), 64 if op.brush_strength > 1 else 36 if op.brush_strength > .5 else 16, 1.5, (1, 1, 0, 1))
            _RstLineSBlend()
        
    
    # Line marks
    SetLineSBlend(2.5)
    mark_rad = op.rad+4*dpi
    mark_co = (.7, .7, .7, .92)
    text_off = -10*dpi
    # Size Mid.
    start = Vector((o.x, o.y+mark_rad))
    mid = rotate_point_around_point(o, start, radians(45))
    direction = direction_from_to(o, mid)
    DiL(mid, mid+direction*10, mark_co)
    if op.is_sliding_type == SIZE:
        p = mid+direction*(text_off*8)
        Draw_Text_AlignCenter(*p, str(op.brush_size), ts_12*2)
    Draw_Text_Right(*(mid+direction*text_off), '100', ts_10)
    # Size Top.
    direction = direction_from_to(o, start)
    DiL(start, start+direction*10, mark_co)
    Draw_Text_AlignCenter(*(start+direction*(text_off*1.2)), '0', ts_10)
    # Size Bot.
    start = Vector((o.x+mark_rad, o.y))
    mid = rotate_point_around_point(o, start, radians(-45)-radians(135))
    direction = direction_from_to(o, mid)
    DiL(mid, mid+direction*10, mark_co)
    Draw_Text_Right(*(mid+direction*text_off), '500', ts_10)
    # Size Bot2.
    p = rotate_point_around_point(o, mid, radians(-45/2))
    direction = direction_from_to(o, p)
    DiL(p, p+direction*10, mark_co)
    Draw_Text_Right(*(p+direction*text_off), '250', ts_10)
    # Strenght Mid.
    start = o + Vector((mark_rad, 0))
    mid = rotate_point_around_point(o, start, radians(-45))
    direction = direction_from_to(o, mid)
    DiL(mid, mid+direction*10, mark_co)
    if op.is_sliding_type == STRENGHT:
        p = mid+direction*(text_off*8)
        Draw_Text_AlignCenter(*p, str(round(op.brush_strength, 2)), ts_12*2)
    Draw_Text(*(mid+direction*text_off), '1.0', ts_10)
    # Strenght Top.
    direction = direction_from_to(o, start)
    DiL(start, start+direction*10, mark_co)
    Draw_Text(*(start+direction*text_off), '0.0', ts_10)
    # Strenght Bot.
    end = o - Vector((0, mark_rad))
    direction = direction_from_to(o, end)
    DiL(end, end+direction*10, mark_co)
    Draw_Text_AlignCenter(*(end+direction*text_off), '2.0', ts_10)
    
    # Preview.
    start = o + Vector((mark_rad*1.15, 0))
    p = rotate_point_around_point(o, start, radians(45))#-angle_diff))
    if op.coloring:
        s = -text_off*1.5
        c = op.prev_color
        p = p + Vector((s*1.15, -s*.75))
        DiCFCL(p, s*.75, (pow(c[0], 2.2), pow(c[1], 2.2), pow(c[2], 2.2), 1), (0, 0, 0, 1))

    c = op.color
    p = rotate_point_around_point(o, start, radians(45))
    DiCFCL(p, -text_off*1.5, (pow(c[0], 2.2), pow(c[1], 2.2), pow(c[2], 2.2), 1), (0, 0, 0, 1))
    
    # Arcs.
    ss_circle_rad = op.rad+3*dpi
    # Size.
    DiRNGBLRSLC(o, ss_circle_rad, .018, (0, .5, 0, .5), (.9, .9, .9, .9))
    handle = op.handle_size
    DiCFS(handle, 10*dpi, (.36, .36, .36, 1))
    # Strenght.
    DiRNGBLRSLC(o, ss_circle_rad, .018, (.5, 1, .5, 1), (.9, .9, .9, .9))
    handle = op.handle_strenght
    DiCFS(handle, 10*dpi, (.36, .36, .36, 1))


    _SetLineSBlend(2.2)
    DiCLS(op.handle_size, 10*dpi, 20, 2.2, (.1, .1, .1, 1))
    DiCLS(op.handle_strenght, 10*dpi, 20, 2.2, (.1, .1, .1, 1))
    _RstLineSBlend()
    
    RstBlend()
    RstLineSBlend()
