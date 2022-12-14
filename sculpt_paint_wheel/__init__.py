# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from . import auto_load
bl_info = {
    "name": "Sculpt+Paint Wheel",
    "author": "J. Fran Matheu (@jfranmatheu)",
    "description": "Enhance your workflow with this awesome sculpt+paint wheel!",
    "blender": (3, 3, 0),
    "version": (3, 0, 0),
    "location": "Hold 'Space' inside 3D Viewport in Sculpt/Texture/Vertex/Weight modes. // 3D Viewport > Sidebar ('N') > 'Sculpt'/'Paint' tab > 'Sculpt Wheel'/'Paint Wheel'",
    "warning": "Versions are X.Y.Z, where X is for main version, Y for subversion (bugfixes) and Z for alpha/beta development (0 on release versions).",
    "category": "Interface"
}

auto_load.init()


def gen_config():
    from . file_manager import user_data
    from pathlib import Path
    addon_data_path = Path(user_data)
    if not addon_data_path.exists():
        addon_data_path.mkdir(parents=True, exist_ok=True)
    from . file_manager import UserData
    from os import makedirs
    makedirs(UserData.GLOB_SCULPT_TOOLSETS_DIR(), exist_ok=True)
    makedirs(UserData.BACKUP_DIR(), exist_ok=True)
    makedirs(UserData.EXPORT_SCULPT_TOOLSETS_DIR(), exist_ok=True)
    makedirs(UserData.EXPORT_SCULPT_BUTTONS_DIR(), exist_ok=True)
    makedirs(UserData.EXPORT_SCULPT_BUTTON_ICONS_DIR(), exist_ok=True)

def register():
    gen_config()

    #from .icons import load_icons
    # load_icons()

    from bpy.utils import register_class

    auto_load.register()  # REGISTER OPERATORS...

    '''

    from .addon import register as register_prefs
    register_prefs(register_class)
    '''
    from .data import register as register_data
    register_data(register_class)

    from .ui.ui import register as register_ui
    register_ui(register_class)

    #from .op import register as register_ops
    # register_ops(register_class)

    #from . gizmo_test import TEST_GG_gizmo_group, MyCustomShapeWidget
    # register_class(MyCustomShapeWidget)
    # register_class(TEST_GG_gizmo_group)

    #from . handlers import register_handlers
    #register_handlers()


def unregister():
    from bpy.utils import unregister_class

    #from . handlers import unregister_handlers
    #unregister_handlers()

    from .ui.ui import unregister as unregister_ui
    unregister_ui(unregister_class)

    from .data import unregister as unregister_data
    unregister_data(unregister_class)
    '''
    from .addon import unregister as unregister_prefs
    unregister_prefs(unregister_class)
    '''

    #from .op import register as unregister_ops
    # unregister_ops(unregister_class)

    #from .icons import remove_icons
    # remove_icons()

    auto_load.unregister()  # UNREGISTER OPERATORS...

    #from . gizmo_test import TEST_GG_gizmo_group, MyCustomShapeWidget
    # unregister_class(TEST_GG_gizmo_group)
    # unregister_class(MyCustomShapeWidget)
