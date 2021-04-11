from enum import Enum
from ... utils import load_image


class DefToolImage(Enum):
    # COMMON TOOLS.
    T_SELECT_BOX = "Select_Box"
    T_SELECT_TWEAK = "Select_Tweak"
    
    # WEIGHT PAINT MODE.
    PAINT_DRAW = "Paint_Draw"
    PAINT_BLUR = "Paint_Blur"
    PAINT_AVERAGE = "Paint_Average"
    PAINT_SMEAR = "Paint_Smear"
    PAINT_GRADIENT = "Paint_Gradient"
    PAINT_SAMPLE_WEIGHT = "Paint_Sample_Weight"
    PAINT_SAMPLE_VERTEX_GROUP = "Paint_Sample_Vertex_Group"
    
    # SCULPT MDOE
    DEFAULT = "Default_icon"
    DRAW = 'Draw_icon'
    DRAW_SHARP = 'Draw_Sharp_icon'
    CLAY = 'Clay_icon'
    CLAY_STRIPS = 'Clay_Strips_icon'
    CLAY_THUMB = 'Clay_Thumb_icon'
    LAYER = 'Layer_icon'
    INFLATE = 'Inflate_icon'
    BLOB = 'Blob_icon'
    CREASE = 'Crease_icon'
    SMOOTH = 'Smooth_icon'
    FLATTEN = 'Flatten_icon'
    FILL = 'Fill_icon'
    SCRAPE = 'Scrape_icon'
    MULTIPLANE_SCRAPE = 'Scrape_MultiPlane_icon'
    PINCH = 'Pinch_icon'
    GRAB = 'Grab_icon'
    ELASTIC_DEFORM = 'ElasticDeform_icon'
    SNAKE_HOOK = 'SnakeHook_icon'
    THUMB = 'Thumb_icon'
    POSE = 'Pose_icon'
    NUDGE = 'Nudge_icon'
    ROTATE = 'Rotate_icon'
    #TOPOLOGY = 'Topology_icon'
    #BOUNDARY = 'Boundary_icon'
    CLOTH = 'Cloth_icon'
    SIMPLIFY = 'Simplify_icon'
    MASK = 'Mask_icon'
    #PAINT = 'Paint_icon'
    #SMEAR = 'Paint_Smear_icon'
    DRAW_FACE_SETS = 'Draw_FaceSets_icon'
    
    T_MESH_FILTER = 'Filter_Mesh_icon'
    T_CLOTH_FILTER = 'Filter_Cloth_icon'
    
    T_BOX_MASK = 'Box_Mask_icon'
    T_BOX_HIDE = 'Box_Hide_icon'
    T_LASSO_MASK = 'Lasso_Mask_icon'
    
    T_TRANSFORM = 'Transform_icon'
    T_MOVE = 'Move_icon'
    T_ROTATE = '_Rotate_icon'
    T_SCALE = 'Scale_icon'
    
    T_ANNOTATE = 'Annotate_icon'
    
    # 2.91
    BOUNDARY = 'Boundary_icon'
    DISPLACEMENT_ERASER = 'Displacement_Eraser_icon'
    T_LINE_MASK = 'Line_Mask_icon'
    T_BOX_FACE_SET = 'Box_FaceSet_icon'
    T_LASSO_FACE_SET = 'Lasso_FaceSet_icon'
    T_BOX_TRIM = 'Box_Trim_icon'
    T_LASSO_TRIM = 'Lasso_Trim_icon'
    T_LINE_PROJECT = 'Line_Project_icon'
    T_FACE_SET_EDIT = 'Edit_FaceSet_icon'

    def __call__(self):
        return load_image(self.value, '.png', 'tools')

def get_tool_icon(tool, is_brush=True):
    if is_brush:
        attr = getattr(DefToolImage, tool.sculpt_tool, None)
    else:
        name = 'T_' + tool.split('.')[1].upper()
        #print(name)
        attr = getattr(DefToolImage, name, None)
    #print("ATTR:", attr)
    if not attr:
        return None
    return attr()
