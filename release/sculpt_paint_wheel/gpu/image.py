from . state import SetBlend, RstBlend
from . gpu_shaders import Shader2D, ShaderType
from bgl import glActiveTexture, glBindTexture, GL_TEXTURE_2D, GL_TEXTURE0
from . dibuix import bat


img_shader = Shader2D.IMAGE()
tex_coord = ((0, 0), (1, 0), (1, 1), (0, 1))
def verts(p, s):
    x, y = p
    w, h = s
    return ((x,y),(x+w,y),(x+w,y+h),(x,y+h))


def Draw_Image(_p, _s, _i, shader=img_shader):
    b = bat(shader, ShaderType.TRIFAN(), {'pos':verts(_p, _s), 'texCoord':tex_coord})
    SetBlend()
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, _i)
    shader.bind()
    shader.uniform_int("image", 0)
    b.draw(shader)
    RstBlend()
