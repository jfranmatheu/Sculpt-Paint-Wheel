import re
import bpy
import gpu
from gpu.shader import from_builtin#, code_from_builtin # NOTE: Exposes the internal shader code for query.
from gpu.types import GPUShader
from enum import Enum


class ShaderName2D(Enum):
    IMAGE   = 'IMAGE'
    UNIFORM = 'UNIFORM_COLOR'
    FLAT    = 'FLAT_COLOR'
    SMOOTH  = 'SMOOTH_COLOR'

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
    UNIFORM = 'UNIFORM_COLOR'
    FLAT    = 'FLAT_COLOR'
    SMOOTH  = 'SMOOTH_COLOR'

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

class BuiltinShaderName(Enum):
    IMAGE   = 'IMAGE'
    UNIFORM = 'UNIFORM_COLOR'
    FLAT    = 'FLAT_COLOR'
    SMOOTH  = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value

builtin_shader_image         = from_builtin(BuiltinShaderName.IMAGE())
builtin_shader_color_unif    = from_builtin(BuiltinShaderName.UNIFORM())
builtin_shader_color_flat    = from_builtin(BuiltinShaderName.FLAT())
builtin_shader_color_smooth  = from_builtin(BuiltinShaderName.SMOOTH())

class BuiltinShader(Enum):
    IMAGE   = builtin_shader_image
    UNIFORM = builtin_shader_color_unif
    FLAT    = builtin_shader_color_flat
    SMOOTH  = builtin_shader_color_smooth

    def __call__(self):
        return self.value


class Shader2D(Enum):
    IMAGE   = shader_2d_image
    UNIFORM = shader_2d_color_unif
    FLAT    = shader_2d_color_flat
    SMOOTH  = shader_2d_color_smooth

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

def Shader(*shaders) -> GPUShader:
    try:
        if bpy.app.version >= (5, 0):
            new_shader = _create_shader_50(*shaders)
        else:
            new_shader = GPUShader(*shaders)
    except Exception as e:
        print("----------------------------------------------------------------")
        print("ERROR! Couldn't create GPUShader:")
        print(e)
        print("----------------------------------------------------------------")
        return None
    return new_shader


def _strip_shader_declarations(source: str) -> str:
    cleaned = []
    skip_depth = 0
    for line in source.splitlines():
        stripped = line.strip()
        if skip_depth:
            skip_depth += line.count("{") - line.count("}")
            continue
        if stripped.startswith("float linearrgb_to_srgb(") or stripped.startswith("void linearrgb_to_srgb("):
            skip_depth = line.count("{") - line.count("}")
            if skip_depth <= 0:
                skip_depth = 1
            continue
        if not stripped:
            cleaned.append(line)
            continue
        if stripped.startswith("uniform "):
            continue
        if stripped.startswith("in "):
            continue
        if stripped.startswith("out "):
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def _iter_uniforms(*sources):
    seen = set()
    for source in sources:
        for uniform_type, uniform_name in re.findall(r"uniform\s+([A-Za-z0-9_]+)\s+([A-Za-z0-9_]+)\s*;", source):
            key = (uniform_type, uniform_name)
            if key in seen:
                continue
            seen.add(key)
            yield uniform_type, uniform_name


def _create_shader_50(vertex_source: str, fragment_source: str, geometry_source=None, libcode=None, defines=None):
    if geometry_source is not None:
        raise RuntimeError("Geometry shaders are not supported by the Blender 5.x compatibility path")

    shader_info = gpu.types.GPUShaderCreateInfo()

    if "texco_interp" in vertex_source:
        vert_out = gpu.types.GPUStageInterfaceInfo("spw_iface")
        vert_out.smooth('VEC2', "texco_interp")
        shader_info.vertex_in(0, 'VEC2', "p")
        shader_info.vertex_in(1, 'VEC2', "texco")
        shader_info.vertex_out(vert_out)
    else:
        shader_info.vertex_in(0, 'VEC2', "p")

    shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")

    sampler_slot = 0
    for uniform_type, uniform_name in _iter_uniforms(vertex_source, fragment_source):
        if uniform_name == "ModelViewProjectionMatrix":
            continue
        if uniform_type == "sampler2D":
            shader_info.sampler(sampler_slot, 'FLOAT_2D', uniform_name)
            sampler_slot += 1
            continue
        if uniform_type == "float":
            shader_info.push_constant('FLOAT', uniform_name)
            continue
        if uniform_type == "int":
            shader_info.push_constant('INT', uniform_name)
            continue
        if uniform_type == "vec3":
            shader_info.push_constant('VEC3', uniform_name)
            continue
        if uniform_type == "vec4":
            shader_info.push_constant('VEC4', uniform_name)
            continue

    shader_info.fragment_out(0, 'VEC4', "fragColor")
    shader_info.vertex_source(_strip_shader_declarations(vertex_source))
    shader_info.fragment_source(_strip_shader_declarations(fragment_source))
    return gpu.shader.create_from_info(shader_info)

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
    RNGBLRANG=Shader(*SHCx524E47424C521197)
    # IMGA_LINE = Shader(*SHCx494D47415F4C494E45)

    def __call__(self):
        return self.value
