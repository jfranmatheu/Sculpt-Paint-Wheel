from enum import Enum
import bpy

class CursorIcon(Enum):
    DEFAULT       =      'DEFAULT'
    NONE          =         'NONE'
    WAIT          =         'WAIT'
    CROSSHAIR     =    'CROSSHAIR'
    MOVE_X        =       'MOVE_X'
    MOVE_Y        =       'MOVE_Y'
    KNIFE         =        'KNIFE'
    TEXT          =         'TEXT'
    PAINT_BRUSH   =  'PAINT_BRUSH'
    PAINT_CROSS   =  'PAINT_CROSS'
    HAND          =         'HAND'
    SCROLL_X      =     'SCROLL_X'
    SCROLL_Y      =     'SCROLL_Y'
    EYEDROPPER    =   'EYEDROPPER'
    DOT           =          'DOT'
    ERASER        =       'ERASER'

class Cursor:
    @staticmethod
    def set_icon(context, cursor = CursorIcon.DEFAULT):
        if not context: context = bpy.context
        context.window.cursor_modal_set(cursor.value)

    @staticmethod
    def wrap(x, y, context=bpy.context):
        context.window.cursor_warp(int(x), int(y))
