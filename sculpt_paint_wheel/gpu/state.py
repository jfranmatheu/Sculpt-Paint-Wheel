from gpu.state import *

__all__ = [
'GetActiveFrameBuffer',
'GetViewport',
'SetViewport',

'SetBlend',
'GetBlend',
'RstBlend',

'SetDepth',
'SetDepthAlways',
'SetDepthNone',
'RstDepth',

'SetUseProgramPointSize',
'RstUseProgramPointSize',
'SetPoint',
'RstPoint',
'SetPointBlend',
'RstPointBlend',

'SetLine',
'RstLine',
'SetLineBlend',
'RstLineBlend',
'SetLineSBlend', # backward compat.
'RstLineSBlend', # backward compat.

'SetSRGB',
'RstColorSpace'
]

def GetActiveFrameBuffer():return framebuffer_active_get()
def GetViewport():return viewport_get()
def SetViewport(x,y,width,height):viewport_set(x,y,width,height)

def SetBlend(mode: str = 'ALPHA'):blend_set(mode)
def GetBlend():return blend_get()
def RstBlend():SetBlend('NONE')

def SetDepth(mode: str = 'LESS_EQUAL'):depth_test_set(mode);depth_mask_set(True)
def SetDepthAlways():SetDepth('ALWAYS')
def SetDepthNone():SetDepth('NONE')
def RstDepth():depth_mask_set(False)

def SetUseProgramPointSize(ps):program_point_size_set(True)
def RstUseProgramPointSize(ps):program_point_size_set(False)
def SetPoint(ps):point_size_set(ps)
def RstPoint():point_size_set(1.0)
def SetPointBlend(ps):SetBlend();SetPoint(ps)
def RstPointBlend():RstBlend();RstPoint()

def SetLine(lt):line_width_set(lt)
def RstLine():SetLine(1.0)
def SetLineBlend(lt):SetBlend();SetLine(lt)
def RstLineBlend():RstBlend();RstLine()
def SetLineSBlend(lt):SetLineBlend(lt)  # backward compat.
def RstLineSBlend():RstLineBlend()      # backward compat.


from bpy.app import version
if version[0] == 2 and version[1] <= 93:
    from bgl import *

    def SetSRGB():glEnable(GL_FRAMEBUFFER_SRGB)
    def RstColorSpace():glDisable(GL_FRAMEBUFFER_SRGB)

else:
    def SetSRGB():pass
    def RstColorSpace():pass
