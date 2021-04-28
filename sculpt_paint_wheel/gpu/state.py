from bpy.app import version
if version[0] <= 2 and version[1] < 93:
    pass

else:
    # BUG. NEW API GIVE WRONG RESULTS LMAO...
    from gpu import state


    __all__ = [
    'SetPoint',
    'RstPoint',
    'SetPointBlend',
    'RstPointBlend',
    'SetLine',
    'RstLine',
    'SetLineSBlend',
    'RstLineSBlend',
    'SetBlend',
    'GetBlend',
    'RstBlend',
    'SetDepth',
    'RstDepth'
    ]

    def SetPointSize(ps):state.point_size_set(ps)
    def SetPoint(ps):state.program_point_size_set(True);SetPointSize(ps)
    def RstPoint():state.program_point_size_set(False);SetPointSize(1.0)
    def SetPointBlend(ps):SetBlend();SetPoint(ps)
    def RstPointBlend():RstBlend();RstPoint()
    def SetLine(lt):state.line_width_set(lt)
    def RstLine():SetLine(1.0)
    def SetLineSBlend(lt):SetBlend();SetLine(lt)
    def RstLineSBlend():RstBlend();RstLine()
    def SetBlend(mode: str = 'ALPHA'):state.blend_set(mode)
    def GetBlend():return state.blend_get()
    def RstBlend():SetBlend('NONE')
    def SetDepth(mode: str = 'NONE'):state.depth_test_set(mode)  #state.depth_mask_set(False);
    def RstDepth():SetDepth('LESS_EQUAL') #state.depth_mask_set(True);
