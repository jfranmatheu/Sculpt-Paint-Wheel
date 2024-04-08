# from sculpt_paint_wheel.data import SculptWheelData as _SculptWheelData

import bpy


class Props:
    def SculptWheelData(context) -> '_SculptWheelData':
        if 'spwheel' in context.scene:
            return context.scene.sculpt_wheel
        for scene in bpy.data.scenes:
            if 'spwheel' in scene:
                return scene.sculpt_wheel
        try:
            context.scene['spwheel'] = 1
        except AttributeError:
            pass
        return context.scene.sculpt_wheel
