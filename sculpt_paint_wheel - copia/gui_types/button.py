from .. utils import point_inside_circle
from .. gpu.dibuix import DiCFS, DiRNGBLR, DiIMGA


class ButtonCircle:
    def __init__(self, pos, rad, co, i, fun, *args):
        self.pos = pos
        self.rad = rad
        self.co = co
        self.act_co = (.34, .5, .76, 1)
        self.id = i
        self.fun = fun
        self.args = args
        self.on_hover = False
        self.toggle = False

    def check(self, mouse):
        self.on_hover = point_inside_circle(mouse, self.pos, self.rad)
        return self.on_hover

    def __call__(self, context):
        if self.args:
            self.fun(self.args)
        else:
            self.fun()
        self.toggle = not self.toggle

    def draw(self):
        if self.on_hover:
            DiCFS(self.pos, self.rad, self.act_co if self.toggle else self.co)
            DiRNGBLR(self.pos, self.rad, .1, .025, (0, 1, 1, .9))
        else:
            DiCFS(self.pos, self.rad, self.act_co if self.toggle else self.co)
            DiRNGBLR(self.pos, self.rad, .1, .025, (.4, .4, .4, .9))
        if self.id:
            rad = self.rad*.7
            DiIMGA((self.pos[0]-rad, self.pos[1]-rad), [rad*2]*2, self.id)
