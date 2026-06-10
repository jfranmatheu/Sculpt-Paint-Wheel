import sys
import pathlib
import tempfile
from enum import Enum
from os.path import join, dirname, exists, isdir
from os import mkdir

import bpy

b3d_user_path = bpy.utils.resource_path('USER')
b3d_config_path = join(b3d_user_path, "config")

b3d_appdata_path = dirname(bpy.utils.resource_path('USER'))

r"""
* Linux *
LOCAL: ./3.1/
USER: $HOME/.config/blender/3.1/
SYSTEM: /usr/share/blender/3.1/
-----
* Mac OS *
LOCAL: ./3.1/
USER: /Users/$USER/Library/Application Support/Blender/3.1/
SYSTEM: /Library/Application Support/Blender/3.1/
-----
* Windows *
LOCAL: .\3.1\
USER: %USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\3.1\
SYSTEM: %USERPROFILE%\AppData\Roaming\Blender Foundation\Blender\3.1\
"""


def get_addondatadir() -> pathlib.Path:

    '''
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    '''

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Blender Foundation/Blender/addon_data"
    elif sys.platform == "linux":
        return home / ".local/share/blender/addon_data"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Blender/addon_data"

    '''
    import os

    configpath = os.path.join(
        os.environ.get('APPDATA') or
        os.environ.get('XDG_CONFIG_HOME') or
        os.path.join(os.environ['HOME'], '.config'),
        "Blender Foundation"
    )
    print(configpath)
    '''


def resolve_user_data_path() -> pathlib.Path:
    candidates = []

    if sys.platform == "win32":
        appdata = pathlib.Path.home() / "AppData" / "Roaming"
        candidates.append(appdata / "Blender Foundation" / "Blender" / "addon_data" / "spwheel")
        candidates.append(pathlib.Path(bpy.utils.resource_path('USER')) / "addon_data" / "spwheel")
    elif sys.platform == "linux":
        candidates.append(pathlib.Path.home() / ".local" / "share" / "blender" / "addon_data" / "spwheel")
        candidates.append(pathlib.Path(bpy.utils.resource_path('USER')) / "addon_data" / "spwheel")
    elif sys.platform == "darwin":
        candidates.append(pathlib.Path.home() / "Library" / "Application Support" / "Blender" / "addon_data" / "spwheel")
        candidates.append(pathlib.Path(bpy.utils.resource_path('USER')) / "addon_data" / "spwheel")

    candidates.append(pathlib.Path(tempfile.gettempdir()) / "spwheel")

    for path in candidates:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except (PermissionError, OSError):
            continue

    return pathlib.Path(tempfile.gettempdir()) / "spwheel"


# HARDCODED. Change this to change root of user data.
user_data = str(resolve_user_data_path())

class UserData(Enum):
    ROOT = user_data

    ''' Export paths. '''
    EXPORT_DIR                  = join(user_data, 'export')
    EXPORT_SCULPT_DIR           = join(user_data, 'export', 'sculpt')
    EXPORT_SCULPT_TOOLSETS_DIR  = join(user_data, 'export', 'sculpt', 'toolsets')
    EXPORT_SCULPT_BUTTONS_DIR   = join(user_data, 'export', 'sculpt', 'buttons')
    EXPORT_SCULPT_BUTTON_ICONS_DIR = join(user_data, 'export', 'sculpt', 'buttons', 'icons')

    ''' Global data paths. '''
    GLOB_DIR                    = join(user_data, 'shared')
    GLOB_SCULPT_DIR             = join(user_data, 'shared', 'sculpt')
    GLOB_SCULPT_TOOLSETS_DIR    = join(user_data, 'shared', 'sculpt', 'toolsets')
    GLOB_SCULPT_TOOLSETS_FILE   = join(user_data, 'shared', 'sculpt', 'toolsets.json')
    GLOB_SCULPT_BUTTONS_FILE    = join(user_data, 'shared', 'sculpt', 'buttons.json')

    ''' BACKUP path. '''
    BACKUP_DIR = join(user_data, 'backups')

    def __call__(self, *args):
        if args:
            path = join(self.value, *args)
        path = self.value
        if not exists(path) and isdir(path):
            mkdir(path)
        return path
