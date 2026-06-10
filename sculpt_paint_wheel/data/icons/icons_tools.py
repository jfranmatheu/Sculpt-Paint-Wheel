import bpy
import hashlib

from enum import Enum
from ... utils import load_image
from ...utils.compat import get_sculpt_brush_type


_BRUSH_TOOL_NAME_TO_ENUM = {
    "Multi-plane Scrape": "MULTIPLANE_SCRAPE",
    "Elastic Grab": "ELASTIC_DEFORM",
    "Scrape Multiplane": "MULTIPLANE_SCRAPE",
    "Multiplane Scrape": "MULTIPLANE_SCRAPE",
    "Scrape/Peaks": "SCRAPE",
    "Scrape/Fill": "SCRAPE",
    "SculptDraw": "DRAW",
    "Inflate/Deflate": "INFLATE",
    "Pinch/Magnify": "PINCH",
    "Crease Sharp": "CREASE",
    "Grab Cloth": "CLOTH",
    "Drag Cloth": "GRAB",
    "Inflate Cloth": "INFLATE",
    "Push Cloth": "NUDGE",
    "Expand/Contract Cloth": "ELASTIC_DEFORM",
}


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

    # 2.92-3
    DISPLACEMENT_SMEAR = 'Displacement_Smear_icon'
    TOPOLOGY = 'Slide_Relax_icon'

    # 3.X
    T_MASK_BY_COLOR = 'MaskByColor_icon'
    T_COLOR_FILTER = 'ColorFilter_icon'

    def __call__(self):
        return load_image(self.value, '.png', 'tools')


_ASSET_PREVIEW_IMAGE_PREFIX = ".sculpt_wheel_asset_preview_"


def _build_preview_cache_key(brush, preview):
    # Use preview pixel signature so brushes with identical names still get unique icons.
    icon_pixels = getattr(preview, "icon_pixels_float", None)
    if icon_pixels:
        sample = bytes(bytearray(max(0, min(255, int(v * 255.0))) for v in list(icon_pixels)))
        if sample:
            return hashlib.sha1(sample).hexdigest()

    image_pixels = getattr(preview, "image_pixels_float", None)
    if image_pixels:
        head = list(image_pixels)[:4096]
        sample = bytes(bytearray(max(0, min(255, int(v * 255.0))) for v in head))
        if sample:
            return hashlib.sha1(sample).hexdigest()

    return str(getattr(brush, "as_pointer", lambda: id(brush))())


def _get_brush_preview_image(brush):
    if brush is None:
        return None

    preview = getattr(brush, "preview", None)
    if preview is None:
        return None

    size = tuple(getattr(preview, "image_size", (0, 0)))
    if len(size) != 2 or size[0] <= 0 or size[1] <= 0:
        return None

    pixels = getattr(preview, "image_pixels_float", None)
    if pixels:
        pixels = list(pixels)
    else:
        pixels = getattr(preview, "image_pixels", None)
        if not pixels:
            return None
        pixels = [value / 255.0 for value in pixels]

    expected_len = size[0] * size[1] * 4
    if len(pixels) < expected_len:
        return None

    preview_key = _build_preview_cache_key(brush, preview)
    image_name = _ASSET_PREVIEW_IMAGE_PREFIX + preview_key

    image = bpy.data.images.get(image_name)
    if image is None or tuple(image.size) != size:
        if image is not None:
            bpy.data.images.remove(image)
        image = bpy.data.images.new(image_name, width=size[0], height=size[1], alpha=True)

    image.pixels = pixels[:expected_len]
    return image


def get_tool_icon(tool, is_brush=True):
    if is_brush:
        preview_image = _get_brush_preview_image(tool)
        if preview_image is not None:
            return preview_image

        attr = None
        brush_type = get_sculpt_brush_type(tool)
        if tool is not None:
            tool_name = str(getattr(tool, "name", "")).replace("SW | ", "").strip()
            normalized_name = tool_name.upper().replace("/", "_").replace("-", "_").replace(" ", "_")
            normalized_name = normalized_name.replace("|", "_")
            while "__" in normalized_name:
                normalized_name = normalized_name.replace("__", "_")
            mapped_name = _BRUSH_TOOL_NAME_TO_ENUM.get(tool_name, None)
            candidates = [normalized_name, normalized_name.removeprefix("SW_"), normalized_name.removeprefix("SW__")]
            if mapped_name:
                candidates.insert(0, mapped_name)
            for candidate in candidates:
                attr = getattr(DefToolImage, candidate, None)
                if attr:
                    break
        if not attr:
            attr = getattr(DefToolImage, brush_type, None)
        if not attr and brush_type in {"PAINT", "SMEAR"}:
            attr = getattr(DefToolImage, "DRAW", None)
    else:
        raw_name = tool.split('.', 1)[1]
        if tool.startswith("builtin_brush."):
            normalized_name = _BRUSH_TOOL_NAME_TO_ENUM.get(raw_name, raw_name.upper().replace("/", "_").replace("-", "_").replace(" ", "_"))
            while "__" in normalized_name:
                normalized_name = normalized_name.replace("__", "_")
            attr = getattr(DefToolImage, normalized_name, None)
        else:
            name = 'T_' + raw_name.upper()
            attr = getattr(DefToolImage, name, None)
    # print("ATTR:", attr)
    if not attr:
        print("Could not find icon for tool:", tool)
        return None
    return attr()
