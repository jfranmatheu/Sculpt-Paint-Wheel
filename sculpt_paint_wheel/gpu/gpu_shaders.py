from gpu.shader import from_builtin#, code_from_builtin # NOTE: Exposes the internal shader code for query.
from gpu.types import GPUShader as Shader
from enum import Enum


class ShaderName2D(Enum):
    IMAGE   = '2D_IMAGE'
    UNIFORM = '2D_UNIFORM_COLOR'
    FLAT    = '2D_FLAT_COLOR'
    SMOOTH  = '2D_SMOOTH_COLOR'

    def __call__(self):
        return self.value

'''
NOTE:
Shaders that are embedded in the blender internal code.
They all read the uniform ‘mat4 ModelViewProjectionMatrix’, which can be edited by the ‘gpu.matrix’ module.
For more details, you can check the shader code with the function ‘gpu.shader.code_from_builtin’.

https://docs.blender.org/api/blender2.8/gpu.shader.html?highlight=builtin#gpu.shader.code_from_builtin

'''
# Shader References:
# https://docs.blender.org/api/blender2.8/gpu.html#d-image
# https://docs.blender.org/api/blender2.8/gpu.html#d-rectangle
# https://github.com/lewislepton/shadertutorialseries
# https://github.com/dfelinto/blender/tree/master/source/blender/gpu/shaders
# https://medium.com/@pythor/cool-shaders-f071a491245
from ..__lib__ import *
shader_2d_image         = from_builtin(ShaderName2D.IMAGE())
shader_2d_color_unif    = from_builtin(ShaderName2D.UNIFORM())
shader_2d_color_flat    = from_builtin(ShaderName2D.FLAT())
shader_2d_color_smooth  = from_builtin(ShaderName2D.SMOOTH())

class Shader2D(Enum):
    IMAGE   = shader_2d_image
    UNIFORM = shader_2d_color_unif
    FLAT    = shader_2d_color_flat
    SMOOTH  = shader_2d_color_smooth

    def __call__(self):
        return self.value

class ShaderName3D(Enum):
    UNIFORM = '3D_UNIFORM_COLOR'
    FLAT    = '3D_FLAT_COLOR'
    SMOOTH  = '3D_SMOOTH_COLOR'

    def __call__(self):
        return self.value

shader_3d_color_unif    = from_builtin(ShaderName3D.UNIFORM())
shader_3d_color_flat    = from_builtin(ShaderName3D.FLAT())
shader_3d_color_smooth  = from_builtin(ShaderName3D.SMOOTH())

class Shader3D(Enum):
    UNIFORM = shader_3d_color_unif
    FLAT    = shader_3d_color_flat
    SMOOTH  = shader_3d_color_smooth

    def __call__(self):
        return self.value

class ShaderType(Enum):
    POINTS      = "POINTS"
    LINES       = "LINES"
    TRIS        = "TRIS"
    LINES_ADJ   = "LINES_ADJ"
    TRIFAN      = "TRI_FAN"

    def __call__(self):
        return self.value

# TODO: Make it beautiful, PLEASE...
class SH(Enum):
    PLIGHT = Shader(*SHCx504C49474854)
    CFS_CROPTOP = Shader(*SHCx4346535F43524F50544F50)
    CFS_CROPBOT = Shader(*SHCx4346535F43524F50424F54)
    CFS = Shader(*SHCx434653)
    CFS_GAMMA = Shader(*SHCx434653_2)
    IMGA = Shader(*SHCx494D4741)
    IMGA_GAMMA = Shader(*SHCx494D47415F47414D434F)
    IMGA_GAMMA_INTENSIFY = Shader(*SHCx494D47415F47414D434F5F424F4F5354)
    RNGS_SPLITANG = Shader(*SHCx524E47535F53504C4954414E47)
    RNGBLR = Shader(*SHCx524E47424C52)
    IMGA_GAMMA_OP = Shader(*SHCx494D47415F47414D4D415F4F50)
    RTCROMASLIN=Shader(*SHCx5243524f4d415f534c5f4c494e)
    RGCROMASLIN=Shader(*SHCx4343524F4D415F48)
    RNGBLRSLC=Shader(*SHCx524E47424C5218103)
    RNGCROMALINW=Shader(*SHCx43524e4743524f4d4c494e57)
    # IMGA_LINE = Shader(*SHCx494D47415F4C494E45)

    def __call__(self):
        return self.value
