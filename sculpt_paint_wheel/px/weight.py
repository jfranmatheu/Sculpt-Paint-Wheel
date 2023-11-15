import bpy
from .. gpu.dibuix import *
import colorsys
from .. utils.fun import get_point_in_circle_from_angle, smoothstep, Vector, direction_from_to, distance_between
from math import pi
from .. gpu.text import (
    Draw_Text, Draw_Text_AlignCenter, SetFontSize, GetFontDim
)

from .. gpu.state import SetLineSBlend, RstLineSBlend


DEBUG = False

PI_4 = pi / 4
PI5_4 = 5 * pi / 4
RING = 0
RECT = 1
HORIZONTAL = 0
VERTICAL = 1
NONE = -1
ADD = 0
SUBSTRACT = 1


def draw_callback_px(op, ctx, o):
    if ctx.area != op.ctx_area:
        return

    DiCFS(o, op.rad, op.theme.base_color)

    # Linea del circulo grande.
    #DiCLS(o, op.rad-6, 64, 2., (.4, .4, .4, .95))
    #DiCLS(o, op.rad-8, 64, 2.5, (.05, .05, .05, .95))
    DiRNGBLR(o, op.rad-6, .01, .005, (.24, .24, .24, .95))
    DiRNGBLR(o, op.rad-8, .01, .005, (.05, .05, .05, .95))

    if op.gestual_sabe_dir and op.prefs.gesturepad_mode == 'PREVIEW':
        SetLineSBlend(1.5)
        if (op.gesto_dir == HORIZONTAL and not op.invert_gestodir) or (op.gesto_dir == VERTICAL and op.invert_gestodir):
            value = op.get_brush_strength()
            # max
            DiCLS(o, op.rad-8, 64, 1.5, (.8, .8, .8, .8))
            # mid
            DiCLS(o, op.rad*.5-4, 64, 1.5, (.8, .8, .8, .8))
            # current
            DiCLS(o, (op.rad-8)*(value/2), 64, 1.5, (1, 1, 0, 1))
            # base
            # DiCFCL(o, op.gestual_pad_rad, (.25, .25, .25, .95), (.5, .5, .5, 1))
            # text
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*.64, "Strength", 24)
            # DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15), (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
            Draw_Text_AlignCenter(o[0], o[1], "%.2f" % round(value, 2), 24)
        else:
            value = op.get_brush_size()
            DiCLS(o, value, 64, 1.5, (0, 1, 1, 1))
            Draw_Text_AlignCenter(o[0], o[1]+op.rad*.64, "Size", 24)
            # DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15), (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
            Draw_Text_AlignCenter(o[0], o[1], str(value), 24)
        RstLineSBlend()
        return

    # Anillo.
    #c = colorsys.rgb_to_hsv(0, 1, 1)
    #DiANILLOTONO(o, op.color_ring_rad, float(c[1]), float(c[2]))
    DiANILLOW(o, op.color_ring_rad)

    # RstColorSpace()
    SetBlend()

    if op.wheel.show_markers:
        ts_10 = int(op.text_size*10/12)
        SetLineSBlend(2.2)
        DiLs_((.9, .9, .9, 1), *op.marker_lines)
        RstLineSBlend()
        if op.wheel.use_interactable_markers:
            rad = op.marker_button_rad
            # DiCFCLs(op.marker_button_rad, (.05, .05, .05, .95),
            #        (.4, .4, .4, .95), op.marker_buttons)
            for i, p in enumerate(op.marker_buttons):
                DiCFS(p, rad, (.016, .016, .016, .8))
                DiRNGBLR(p, rad, .08, .01, (.2, .2, .2, .8))
                Draw_Text_AlignCenter(
                    *p, str(round(1-i/op.num_markers, 2)), ts_10)
            if op.on_hover_marker_button is not None:
                # DiCLS(op.marker_buttons[op.on_hover_marker_button],
                #      op.marker_button_rad, 32, 1.7, (1, 0, .9, 1))
                DiRNGBLR(
                    op.marker_buttons[op.on_hover_marker_button], rad, .08, .01, (1, 0, .9, 1))
        else:
            for p, lbl in op.marker_labels:
                Draw_Text_AlignCenter(*p, lbl, ts_10, (1, 1, 1, .8))

    #DiCLS(op.color_handle, 13, 12, 1.3, (1, 1, 1, 1))
    SetLineSBlend(5.2)
    DiL(*op.color_handle_line)
    SetLineSBlend(2.6)
    DiL(*op.color_handle_line, (1, 1, 1, 1))
    RstLineSBlend()

    num_buttons = 8  # len(op.wheel.custom_buttons)
    #DiCFCL(o, op.gestual_pad_rad, op.theme.pad_color if not op.is_gpencil else (.1, .1, .1, .85), (.7, .7, .7, 1))
    DiCFS(o, op.gestual_pad_rad,
          op.theme.pad_color if not op.is_gpencil else (.1, .1, .1, .85))
    #DiRNGBLR(o, op.gestual_pad_rad, .05, .02, (.7, .7, .7, 1))

    if op.gestual:
        #DiCLS(o, op.gestual_pad_rad, 36, 1.5, (1, 0, 1, .95))
        DiRNGBLR(o, op.gestual_pad_rad, .075, .01, (1, 0, 1, .95))
        if not op.gestual_sabe_dir:
            ts = int(op.text_size * 11/12)
            # ⭥ ⇕ ⇳ ᛨ ⭥ 🡙 ↨ ⮃ ⮁ ⇵ ⇅
            Draw_Text_AlignCenter(o[0], o[1]+10, "↕ Size ↕", ts)
            # ⬌ ↔ ⇿ ⭤ ⟷ ⟺ ⬄ � ⮀ ⇆ ⮂ ⇄
            Draw_Text_AlignCenter(o[0], o[1]-10, "↔ Strength ↔", ts)
        elif op.prefs.gesturepad_mode == 'SIMPLE':
            ts_16 = int(op.text_size * 16/12)
            ts_13 = int(op.text_size * 13/12)
            if (op.gesto_dir == HORIZONTAL and not op.invert_gestodir) or (op.gesto_dir == VERTICAL and op.invert_gestodir):
                Draw_Text_AlignCenter(
                    o[0], o[1]+op.gestual_pad_rad*.5, "Strength", ts_13)
                DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15),
                    (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
                Draw_Text_AlignCenter(
                    o[0], o[1]-op.gestual_pad_rad*.3, "%.2f" % round(op.get_brush_strength(), 2), ts_16)
            else:
                Draw_Text_AlignCenter(
                    o[0], o[1]+op.gestual_pad_rad*.5, "Size", ts_13)
                DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15),
                    (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
                Draw_Text_AlignCenter(
                    o[0], o[1]-op.gestual_pad_rad*.3, str(op.get_brush_size()), ts_16)
    elif not op.coloring and (op.is_gpencil or not op.toolbar.hovered_tool and (op.gestual_on_hover or (op.ctrealidx >= num_buttons or op.ctrealidx < 0))):
        Draw_Text_AlignCenter(o[0], o[1], "P A D", int(
            op.text_size * 16/12), (.8, .8, .8, .9), False)
        if op.gestual_on_hover:
            DiRNGBLR(o, op.gestual_pad_rad, .075, .01, (1, 0, 1, .95))
            #DiCLS(o, op.gestual_pad_rad, 36, 1.5, (1, 0, 1, .95))
        else:
            DiRNGBLR(o, op.gestual_pad_rad, .05, .01, (.2, .2, .2, .5))

    if not op.is_gpencil:
        # Ranuras personalizadas.
        #factor = op.gestual_pad_rad / op.color_ring_rad
        # DiRNGS(o, op.color_ring_rad, factor, 1., .5, (.05, .05, .05, .9))
        # DiRNGS_SPLITANG(o, op.tarta_rad, 1., .6, factor,
        #                op.ctnum, op.ctidx, op.theme.pie_color)

        # Botoncitos tarta.
        num_tarta_icons = len(op.tarta_icons)
        Draw_Text(*o, '.', 1, 0, *(.9, .9, .9, .9), False)
        size = Vector((op.tarta_item_rad, op.tarta_item_rad))
        half_size = size / 2.0
        def_bcode = op.none_icon[1]
        is_brush = op.active_tool_is_brush(ctx)
        # for i, b in enumerate(op.wheel.custom_buttons):
        for i in range(0, num_tarta_icons):
            if op.tarta_icons[i]:
                bcode = op.tarta_icons[i][1]  # takes texture. #.bindcode
            else:
                bcode = def_bcode
            DiIMGAMMA_OP(op.tarta_pos[i] - half_size, size,
                         .9 if is_brush or i > 2 else .12, bcode)

        #DiCLS(o, op.tarta_rad, 50, 2, (.75, .75, .75, .9))
        DiRNGBLR(o, op.tarta_rad, .025, .01, (.64, .64, .64, 1))

    text = None
    space = False
    text_size = int(op.text_size)

    '''
    # y = o[1]
    if op.on_hover_tool_index != -1 and op.on_hover_tool_index < num_tools:
        text = tools[op.on_hover_tool_index].name
        text_size = int(text_size * 11/12)
        if len(text) > 12:
            text = text.replace('/', ' ')
            # y += op.gestual_pad_rad / 2
            space = True
        else:
            space = ' ' in text
    '''
    if op.coloring:
        text = "%.2f" % round(op.get_brush_weight(), 2)
        text_size = int(text_size*16/12)
    elif not op.is_gpencil and op.ctidx != -100 and op.ctrealidx > -1 and op.ctrealidx < num_buttons and op.tarta_icons[op.ctrealidx]:
        text = op.wheel.custom_buttons[op.ctrealidx].name
        DiIMGA_Intensify(op.tarta_pos[op.ctrealidx] - half_size,
                         size, op.tarta_icons[op.ctrealidx][1], 1.25)
        # y += op.gestual_pad_rad / 2
        space = ' ' in text
    elif not op.is_gpencil and op.toolbar.hovered_tool:
        #text = "Tool ________ " + op.toolbar.hovered_tool.label
        if op.draw_tool and op.draw_tool == op.toolbar.hovered_tool and op.wheel.use_add_substract_brush and op.draw_tool_toggle != -1:
            text = 'Add' if op.draw_tool_toggle == ADD else 'Subtract'
            text += " (click_to_switch)"
            space = True
        else:
            text = op.toolbar.hovered_tool.label
            space = ' ' in text

    if text:
        if space:
            SetFontSize(0, text_size)
            split = text.split(' ')
            w, h = GetFontDim(0, 'X')
            half_rad = int(op.gestual_pad_rad / 2)
            y = o[1] + half_rad - h
            if len(split) > 2:
                y += (h*.8)
            elif len(split) > 3:
                y += h
            h *= 1.75
            for txt in split:
                Draw_Text_AlignCenter(
                    o[0], y, txt, text_size, (.9, .9, .9, .9), False)
                y -= h
        else:
            Draw_Text_AlignCenter(
                o[0], o[1], text, text_size, (.9, .9, .9, .9), False)

    if op.is_gpencil:
        return

    op.toolbar.draw(int(op.text_size*10/12))

    if op.wheel.use_add_substract_brush and op.draw_tool:
        SetLineSBlend(1.5)
        if op.draw_tool == op.toolbar.active_tool:
            if op.draw_tool_toggle == SUBSTRACT:
                co = (.9, .65, .45, .8) if op.draw_tool.is_on_hover else (.75, .5, .3, .8)
            else:
                co = (.45, .65, .9, .8) if op.draw_tool.is_on_hover else (.3, .5, .75, .8)
        else:
            co = (.24, .24, .24, .8) if op.draw_tool.is_on_hover else (.1, .1, .1, .8)
        if op.draw_tool_toggle == SUBSTRACT:
            lco = (1, .5, .05, 1)
            icon = '─'  # ➖
            offset = Vector((1*op.dpi_factor, -5*op.dpi_factor))
        else:
            lco = (0.05, .5, 1, 1)
            icon = '＋'  # ➕
            offset = Vector((0, 0))
        DiCFCL(op.draw_tool.center, op.toolbar.item_size/2, co, lco)
        Draw_Text_AlignCenter(*op.draw_tool.center+offset,
                              icon, int(op.text_size*24/12))
        RstLineSBlend()
