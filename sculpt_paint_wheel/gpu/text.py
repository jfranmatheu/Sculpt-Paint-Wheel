from blf import (
    enable as text_enable, disable as text_disable,
    SHADOW, shadow as text_shadow, shadow_offset as text_shadow_offset,
    color as text_color, position as text_position, size as text_size,
    dimensions as text_dim, draw as text_draw, ROTATION, rotation as text_rotation,
    clipping as text_clipping, CLIPPING, KERNING_DEFAULT, WORD_WRAP, MONOCHROME
)


def Draw_Text(_x, _y, _text, _size, _font_id = 0, _r = 1, _g = 1, _b = 1, _a = 1, _use_shadow = False):
    if _use_shadow:
        _font_id = 1
        text_enable(_font_id, SHADOW)
        text_shadow(_font_id, 3, 0, 0, 0, .6)
        text_shadow_offset(_font_id, -1, -1)
    text_color(_font_id, _r, _g, _b, _a)
    text_position(_font_id, _x, _y, 0) # -6/-6 para "o" #
    text_size(_font_id, _size, 72)
    text_draw(_font_id, _text)
    if _use_shadow:
        text_disable(_font_id, SHADOW)
        
def Draw_Text_Right(_x, _y, _text, _size, _font_id = 0, _r = 1, _g = 1, _b = 1, _a = 1, _use_shadow = False):
    if _use_shadow:
        _font_id = 1
        text_enable(_font_id, SHADOW)
        text_shadow(_font_id, 3, 0, 0, 0, .6)
        text_shadow_offset(_font_id, -1, -1)
    text_size(_font_id, _size, 72)
    dim = text_dim(_font_id, _text)
    text_color(_font_id, _r, _g, _b, _a)
    text_position(_font_id, _x-dim[0], _y - dim[1]*.5, 0) # -6/-6 para "o" #
    text_draw(_font_id, _text)
    if _use_shadow:
        text_disable(_font_id, SHADOW)

def Draw_Text_AlignCenter(_x=0, _y=0, _text='', _text_size=12, _text_color=(1, 1, 1, 1), _use_shadow=True,  _font_id = 0):
    if _use_shadow:
        _font_id = 1
        text_enable(_font_id, SHADOW)
        text_shadow(_font_id, 3, 0, 0, 0, .6)
        text_shadow_offset(0, -1, -1)
    text_size(_font_id, _text_size, 72)
    dim = text_dim(_font_id, _text)
    text_color(_font_id, *_text_color)
    text_position(_font_id, _x - dim[0]*.5, _y - dim[1]*.5, 0)
    text_draw(_font_id, _text)
    if _use_shadow:
        text_disable(_font_id, SHADOW)