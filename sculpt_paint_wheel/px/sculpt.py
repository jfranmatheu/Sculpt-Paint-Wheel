import bpy
from .. gpu.dibuix import *
import colorsys
from .. utils.fun import get_point_in_circle_from_angle, smoothstep, Vector, direction_from_to, distance_between
from math import pi
from .. gpu.text import (
    Draw_Text, Draw_Text_AlignCenter
)
from .. gpu.image import Draw_Image


DEBUG = False

PI_4 = pi / 4
PI5_4 = 5 * pi / 4
RING = 0
RECT = 1
HORIZONTAL = 0
VERTICAL = 1
NONE = -1

ACTIVE_LINE_COLOR = (pow(.337*1.5, .454545), pow(.5*1.5, .454545), pow(.76*1.5, .454545), 1.)


def draw_callback_px(op, ctx, o):
    if ctx.area != op.ctx_area:
        return

    # Vars.
    tool_rad = op.tool_rad
    half_tool_rad = tool_rad / 2.0
    dec_tool_rad = tool_rad * .9 * op.prefs.tool_icon_scale
    x2_dec_tool_rad = [dec_tool_rad*2]*2
    EDIT_MODE = op.mode == 'EDIT'
    num_icons = len(op.icons)
    custom_co = op.prefs.use_custom_tool_colors

    # Relleno del circulo grande.
    DiCFS(o, op.rad, op.theme.base_color)
    #DiIMGAMMA((0,0), (1,1), 0)
    #DiIMGAMMA_OP((0,0), (1,1), 0.0, 0)
    #DiIMGAMMA((0,0), (1,1), 0)
    #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #SetDepth()
    #SetMultisample()
    #glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, tex)
    #glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, tex)
    RstColorSpace()
    SetBlend()
    
    #glBindTexture(GL_TEXTURE_2D,0)
    #glBindFramebuffer(GL_FRAMEBUFFER, 0)
    #glActiveTexture(GL_TEXTURE0)
    #glHint(GL_TEXTURE_COMPRESSION_HINT, GL_NICEST)
    if EDIT_MODE:
        # Linea del circulo grande. (Modo Edición)
        DiCLS(o, op.rad-8, 64, 1.5, (.95, .5, .15, .95))
        DiCLS(o, op.rad-8, 64, 1.5, (.95, .5, .15, .95))
        
        # Herramientas.
        Draw_Text(*o, '.', 1, 0, *(.9, .9, .9, .9), False)
        
        n = num_icons
        for i, p in enumerate(op.tool_pos):
            if n != 0:
                DiCFCL(p, tool_rad-4, (.12, .12, .12, .9), (.44, .44, .44, .9))
                if op.moving and i == op.moving_tool_index:
                    pass
                else:
                    DiIMGAMMA((p[0] - dec_tool_rad, p[1] - dec_tool_rad), x2_dec_tool_rad, op.icons[i].bindcode)
                n -= 1

        # Modal: estás moviendo una tool de sitio.
        if op.moving and op.moving_tool_index != -1 and op.moving_tool_index < num_icons:
            DiCFCL(op.mouse_pos, dec_tool_rad, (.24, .24, .24, .65), (.8, .8, .8, .2))
            p = (op.mouse_pos[0] - dec_tool_rad, op.mouse_pos[1] - dec_tool_rad)
            
            DiIMGAMMA_OP(p, x2_dec_tool_rad, .8, op.icons[op.moving_tool_index].bindcode)
            if op.moving_remove:
                DiCFCL(op.mouse_pos, dec_tool_rad, (1, 0, 0, .5), (1, .2, .2, .8))

    else:
        tools = op.active_toolset.tools
        num_tools = len(tools)
        # Linea del circulo grande.
        DiCLS(o, op.rad-6, 64, 2., (.4, .4, .4, .95))
        DiCLS(o, op.rad-8, 64, 2.5, (.05, .05, .05, .95))

        if op.gestual_sabe_dir and op.prefs.gesturepad_mode == 'PREVIEW':
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
            return

        # Rueda cromática.
        if op.color:
            # gamco_color = (pow(r, .454545), pow(g, .454545), pow(b, .454545))
            c = colorsys.rgb_to_hsv(*op.color)
            DiANILLOTONO(o, op.color_ring_rad, float(c[1]), float(c[2]))
            DiPKCO(o, op.color_rect_rad, float(c[0]))
            DiCLS(op.handle_h, 3, 12, 1.3, (1, 1, 1, 1))
            DiCLS(op.handle_h, 4, 12, 1.3, (0, 0, 0, 1))
            DiCLS(op.handle_sv, 3, 12, 1.3, (1, 1, 1, 1))
            DiCLS(op.handle_sv, 4, 12, 1.3, (0, 0, 0, 1))
            if op.coloring:
                v = smoothstep(0, 1, 1 - c[2]) # 0 if hsv[2] > .5 else 1
                if op.coloring_type == RING:
                    DiCFCL(op.handle_h, 9, [*op.color, 1], (v, v, v, 1))
                elif op.coloring_type == RECT:
                    DiCFCL(op.handle_sv, 9, [*op.color, 1], (v, v, v, 1))
        # Tool.
        else:
            num_buttons = len(op.wheel.custom_buttons)
            DiCFCL(o, op.gestual_pad_rad, op.theme.pad_color, (.7, .7, .7, 1))
            if op.gestual:
                DiCLS(o, op.gestual_pad_rad, 36, 1.5, (1, 0, 1, .95))
                if not op.gestual_sabe_dir:
                    ts = int(op.text_size * 11/12)
                    Draw_Text_AlignCenter(o[0], o[1]+10, "↕ Size ↕", ts) # ⭥ ⇕ ⇳ ᛨ ⭥ 🡙 ↨ ⮃ ⮁ ⇵ ⇅
                    Draw_Text_AlignCenter(o[0], o[1]-10, "↔ Strength ↔", ts) # ⬌ ↔ ⇿ ⭤ ⟷ ⟺ ⬄ 🡘 ⮀ ⇆ ⮂ ⇄
                elif op.prefs.gesturepad_mode == 'SIMPLE':
                    ts_16 = int(op.text_size * 16/12)
                    ts_13 = int(op.text_size * 13/12)
                    if (op.gesto_dir == HORIZONTAL and not op.invert_gestodir) or (op.gesto_dir == VERTICAL and op.invert_gestodir):
                        Draw_Text_AlignCenter(o[0], o[1]+op.gestual_pad_rad*.5, "Strength", ts_13)
                        DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15), (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
                        Draw_Text_AlignCenter(o[0], o[1]-op.gestual_pad_rad*.3, "%.2f" % round(op.get_brush_strength(), 2), ts_16)
                    else:
                        Draw_Text_AlignCenter(o[0], o[1]+op.gestual_pad_rad*.5, "Size", ts_13)
                        DiL((o[0]-op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15), (o[0]+op.gestual_pad_rad*.75, o[1]+op.gestual_pad_rad*.15))
                        Draw_Text_AlignCenter(o[0], o[1]-op.gestual_pad_rad*.3, str(op.get_brush_size()), ts_16)
            elif op.active_tool_is_brush and (op.gestual_on_hover or ((op.ctrealidx >= num_buttons or op.ctrealidx < 0) and op.on_hover_tool_index == -1)):
                Draw_Text_AlignCenter(o[0], o[1], "P A D", int(op.text_size * 16/12), (.8, .8, .8, .9), False)
                if op.gestual_on_hover:
                    DiCLS(o, op.gestual_pad_rad, 36, 1.5, (1, 0, 1, .95))

            # Ranuras personalizadas.
            factor = op.gestual_pad_rad / op.color_ring_rad
            # DiRNGS(o, op.color_ring_rad, factor, 1., .5, (.05, .05, .05, .9))
            DiRNGS_SPLITANG(o, op.color_ring_rad, factor, 1., .6, op.ctnum, op.ctidx, op.theme.pie_color)

            # Botoncitos de la tarta personalizados.
            num_tarta_icons = len(op.tarta_icons)
            Draw_Text(*o, '.', 1, 0, *(.9, .9, .9, .9), False)
            size = Vector((op.tarta_item_rad, op.tarta_item_rad))
            half_size = size / 2.0
            #for i, b in enumerate(op.wheel.custom_buttons):
            def_bcode = op.none_icon[1]
            for i in range(0, num_tarta_icons):
                if op.tarta_icons[i]:
                    bcode = op.tarta_icons[i].bindcode
                else:
                    bcode = def_bcode
                DiIMGA(op.tarta_pos[i] - half_size, size, bcode)

            DiCLS(o, op.color_ring_rad, 50, 2, (.75, .75, .75, .9))

            text = None
            space = False
            text_size = int(op.text_size)
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

            elif op.ctidx != -100 and op.ctrealidx > -1 and op.ctrealidx < num_tarta_icons and op.tarta_icons[op.ctrealidx]: #num_buttons:
                text = op.wheel.custom_buttons[op.ctrealidx].name
                DiIMGA_Intensify(op.tarta_pos[op.ctrealidx] - half_size, size, op.tarta_icons[op.ctrealidx].bindcode, 1.25)
                # y += op.gestual_pad_rad / 2
                space = ' ' in text

            if text:
                if space:
                    SetFontSize(0, text_size, 72)
                    split = text.split(' ')
                    w, h = GetFontDim(0, 'X')
                    half_rad = int(op.gestual_pad_rad / 2)
                    y = o[1] + half_rad - h
                    if len(split) > 3:
                        y += h
                    h *= 1.75
                    for txt in split:
                        Draw_Text_AlignCenter(o[0], y, txt, text_size, (.9, .9, .9, .9), False)
                        y -= h
                else:
                    Draw_Text_AlignCenter(o[0], o[1], text, text_size, (.9, .9, .9, .9), False)
            

        # Herramientas.
        if not custom_co:
            DiCFCLs(tool_rad-4, (.12, .12, .12, .9), (.44, .44, .44, .9), op.tool_pos)
        else:
            rad = tool_rad-4
            pos = op.tool_pos
            if op.prefs.custom_tool_color_mode == 'FILL':
                for i, tool in enumerate(tools):
                    if tool.color[-1] == 0:
                        DiCFS(pos[i], rad, (.12, .12, .12, .9))
                    else:
                        DiCFS(pos[i], rad, tool.color)
                DiCLSs(rad, 32, 2, (.44, .44, .44, .9), pos)
            else:
                DiCFSs(rad, (.12, .12, .12, .9), pos)
                rad +=2
                for i, tool in enumerate(tools):
                    if tool.color[-1] == 0:
                        DiRNGBLR(pos[i], rad, .08, .02, (.44, .44, .44, .9))
                    else:
                        DiRNGBLR(pos[i], rad, .08, .02, tool.color)

        # Iconos de Herramientas.
        a_idx = op.active_tool_index
        n = num_icons
        for i, p in enumerate(op.tool_pos):
            if n == 0:
                break
            if i == a_idx:
                DiIMGA_Intensify (
                    (p[0] - dec_tool_rad, p[1] - dec_tool_rad),
                    x2_dec_tool_rad,
                    op.icons[a_idx].bindcode, 1.25
                )
            else:
                DiIMGAMMA((p[0] - dec_tool_rad, p[1] - dec_tool_rad), x2_dec_tool_rad, op.icons[i].bindcode)
            n -= 1

        if op.on_hover_tool_index != -1:
            if not op.active_tool_pos or op.on_hover_tool_pos != op.active_tool_pos:
                p = op.on_hover_tool_pos
                if not custom_co:
                    DiCFS(p, tool_rad-4, (.16, .16, .16, .9))
                else:
                    c = tools[op.on_hover_tool_index].color
                    if c[-1] == 0:
                        DiCFS(p, tool_rad-4, (.16, .16, .16, .9))
                    else:
                        color = Vector((c[0], c[1], c[2], c[3])) * 1.25
                        DiCFS(p, tool_rad-4, color)
                if op.on_hover_tool_index != -1 and op.on_hover_tool_index < num_icons:
                    DiIMGA_Intensify (
                        (p[0] - dec_tool_rad, p[1] - dec_tool_rad),
                        x2_dec_tool_rad,
                        op.icons[op.on_hover_tool_index].bindcode, 1.25
                    )

        # Nombres de Herramientas.
        if op.prefs.show_tool_names:

            SetFontWW(0, int(dec_tool_rad * 2))
            for i, p in enumerate(op.tool_pos):
                if i >= num_tools:
                    break
                Draw_Text_AlignCenter(p[0], p[1]-half_tool_rad, tools[i].name, int(op.text_size * 10/12))
            RstFontWW(0)

    # Herramienta sobre el puntero.
    if EDIT_MODE and op.on_hover_tool_pos :
        if not op.active_tool_pos or op.on_hover_tool_pos != op.active_tool_pos:
            DiRNGBLR(op.on_hover_tool_pos, tool_rad-2, .075, .02, (.0, 1., 1., 1.))

    # Herramienta activa.
    if op.active_tool_pos:
        if not custom_co:
            DiRNGBLR(op.active_tool_pos, tool_rad-2, .075, .02, (1, .85, .05, .9))
        else:
            if op.prefs.custom_tool_color_mode == 'FILL':
                DiCLS(op.active_tool_pos, tool_rad, 32, 2, (1, 1, 1, 1))
            else:
                DiRNGBLR(op.active_tool_pos, tool_rad-2, .1, .025, (1, 1, 1, 1))
                DiRNGBLR(op.active_tool_pos, tool_rad, .11, .025, (1, 1, 0, 1))
    
    for b in op.outsider_buttons:
        b.draw()

    if not EDIT_MODE:
        for i, ts in enumerate(op.toolset_pos):
            if op.active_toolset_index == i:
                DiPLight(ts, op.toolset_rad+2, (1, 1, 0))
            else:
                DiPLight(ts, op.toolset_rad, (1, 1, 1))
        if op.on_hover_toolset_pos:
            DiPLight(op.on_hover_toolset_pos, op.toolset_rad+2, (0, 1, 1))

    RstBlend()
    SetSRGB()
