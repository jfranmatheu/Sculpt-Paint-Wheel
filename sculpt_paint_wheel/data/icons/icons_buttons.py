from enum import Enum
from ... utils import load_image
PNG = '.png'
JPG = '.jpg'
BUT_IMAGE = 'buttons'


class ButtonIcon(Enum):
    EDIT = '.Edit'
    NONE = '.None'

    def __call__(self):
        return load_image(self.value, PNG, BUT_IMAGE)

def get_button_icon(icon):
    ico = icon()
    if ico:
        ico.gl_load()
        return ico, ico.bindcode
    return None
