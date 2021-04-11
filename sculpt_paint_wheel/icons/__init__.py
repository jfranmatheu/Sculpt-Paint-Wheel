# ----------------------------------------------------------------- #
# ICONS // PREVIEW COLLECTION
# ----------------------------------------------------------------- #
from os.path import dirname, basename, isfile, join, realpath
import glob
from bpy.utils import previews
from enum import Enum

preview_collections = {}

class Icon(Enum):
    ARROW_UP            =   'arrowUp_icon'
    ARROW_DOWN          =   'arrowDown_icon'
    BMARKET             =   'bMarket_icon'
    BRUSH               =   'brush_icon'
    BRUSH_ADD           =   'brushAdd_icon'
    BRUSH_REMOVE        =   'brushRemove_icon'
    BRUSH_RESET         =   'brushReset_icon'
    BRUSH_SAVE          =   'brushSave_icon'
    CUBEBRUSH           =   'cubebrush_icon'
    DYNTOPO             =   'dyntopo_icon'
    DYNTOPO_BRUSH       =   'dyntopoBrush_icon'
    DYNTOPO_CONSTANT    =   'dyntopoConstant_icon'
    DYNTOPO_RELATIVE    =   'dyntopoRelative_icon'
    DYNTOPO_MANUAL      =   'dyntopoManual_icon'
    DYNTOPO_HIGH        =   'dyntopoHighDetail_icon'
    DYNTOPO_MEDIUM      =   'dyntopoMidDetail_icon'
    DYNTOPO_LOW         =   'dyntopoLowDetail_icon'
    FALLOFF             =   'fallOff_icon'
    FRONTFACES          =   'frontFaces_icon'
    MASK                =   'mask_icon'
    MASK_CAVITY         =   'maskCavity_icon'
    MASK_CLEAR          =   'maskClear_icon'
    MASK_EXTRACT        =   'maskExtractor_icon'
    MASK_INVERT         =   'maskInvert_icon'
    MASK_SHARP          =   'maskSharp_icon'
    MASK_SMOOTH         =   'maskSmooth_icon'
    MASK_TOPOLOGY       =   'maskTopology_icon'
    MIRROR              =   'mirror_icon'
    PAYPAL              =   'paypal_icon'
    RAKE                =   'rake_icon'
    SEPARATOR           =   'separator_icon'
    STROKE              =   'stroke_icon'
    STROKE_AIRBRUSH     =   'strokeAirbrush_icon'
    STROKE_ANCHORED     =   'strokeAnchored_icon'
    STROKE_CURVE        =   'strokeCurve_icon'
    STROKE_DOTS         =   'strokeDots_icon'
    STROKE_DRAGDOT      =   'strokeDragDot_icon'
    STROKE_LINE         =   'strokeLine_icon'
    STROKE_SPACE        =   'strokeSpace_icon'
    TEXTURE             =   'texture_icon'
    TEXTURE_NEW         =   'textureNew_icon'
    TEXTURE_OPEN        =   'textureOpen_icon'

    def __call__(self):
        return preview_collections["main"][self.value].icon_id

def get_icon(icon_idname):
    return preview_collections["main"][icon_idname.value].icon_id

def load_icons():
    print("[SCULPT+PAINT WHEEL] Loading Icons...")
    icons = glob.glob(join(dirname(__file__), "*_icon.png"))
    pcoll = previews.new()

    for img in icons:
        #print(img)
        if isfile(img):
            pcoll.load(basename(img)[:-4], img, 'IMAGE')

    preview_collections["main"] = pcoll

    # DEBUG
    #for key, val in preview_collections["main"].items():
        #print("Key:", key, "Value:", val)

def remove_icons():
    previews.remove(preview_collections["main"])
