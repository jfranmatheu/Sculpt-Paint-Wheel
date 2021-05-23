from . prefs import get_prefs
from . km import get_keyitem, get_keyitem_mode


from . prefs import WheelTheme, ColorPicker, WheelPreferences
CLASSES = (
    WheelTheme, ColorPicker, WheelPreferences
)

def register(reg):
    for cls in CLASSES:
        reg(cls)

def unregister(unreg):
    for cls in reversed(CLASSES):
        unreg(cls)
