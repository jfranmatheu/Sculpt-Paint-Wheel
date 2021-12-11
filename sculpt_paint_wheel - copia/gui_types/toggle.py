from .. utils import point_inside_circle, point_inside_rect, Vector
from .. gpu.dibuix import DiCFCL, DiIMGAMMA


class Toggle:
    def __init__(self, pos, size, co, co_active, i, data, attr):
        self.pos = pos
        self.size = [size]*2 if type(size) not in {tuple, list, Vector} else size
        self.color = co
        self.color_active = co_actives
        self.id = i
        self.data = data
        self.attr = attr

    def check(self, mouse):
        self.on_hover = point_inside_rect(self.pos, self.size)
        return self.on_hover

    def get(self):
        return getattr(self.data, self.attr)

    def set(self, value):
        setattr(self.data, self.attr, value)

    def toggle(self):
        setattr(self.data, self.attr, not self.get())

    def draw(self):
        if self.on_hover:
            DiCFCL(self.pos, self.rad, self.co, (0, 1, 1, .9))
        else:
            DiCFCL(self.pos, self.rad, self.co, (.4, .4, .4, .9))
        if self.id:
            rad = self.rad*.7
            DiIMGAMMA((self.pos[0]-rad, self.pos[1]-rad), [rad*2]*2, self.id)
