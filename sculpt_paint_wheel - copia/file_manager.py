import sys
import pathlib
from enum import Enum
from os.path import join


def get_addondatadir() -> pathlib.Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Blender Foundation/Blender/addon_data"
    elif sys.platform == "linux":
        return home / ".local/share/blender/addon_data"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Blender/addon_data"

# HARDCODED. Change this to change root of user data.
user_data = str((get_addondatadir() / "wheel_user_data").absolute())

class UserData(Enum):
    ROOT = user_data
    
    ''' Export paths. '''
    EXPORT_DIR                  = join(user_data, 'export')
    EXPORT_SCULPT_DIR           = join(user_data, 'export', 'sculpt')
    EXPORT_SCULPT_TOOLSETS_DIR  = join(user_data, 'export', 'sculpt', 'toolsets')
    EXPORT_SCULPT_BUTTONS_DIR   = join(user_data, 'export', 'sculpt', 'buttons')
    
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
            return join(self.value, *args)
        return self.value
