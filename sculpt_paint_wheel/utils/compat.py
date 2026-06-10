import hashlib
import os
import tempfile


def get_sculpt_brush_type(brush):
    if brush is None:
        return None
    return getattr(brush, "sculpt_brush_type", getattr(brush, "sculpt_tool", None))


_SCULPT_BRUSH_TOOL_NAME_MAP = {
    "CLAY_STRIPS": "Clay Strips",
    "CLAY_THUMB": "Clay Thumb",
    "DRAW_FACE_SETS": "Draw Face Sets",
    "DRAW_SHARP": "Draw Sharp",
    "ELASTIC_DEFORM": "Elastic Deform",
    "MULTIPLANE_SCRAPE": "Multi-plane Scrape",
    "SNAKE_HOOK": "Snake Hook",
}

_LEGACY_BRUSH_NAME_TO_TYPE = {
    "SculptDraw": "DRAW",
    "Draw Sharp": "DRAW_SHARP",
    "Clay Strips": "CLAY_STRIPS",
    "Inflate/Deflate": "INFLATE",
    "Crease": "CREASE",
    "Scrape/Peaks": "SCRAPE",
    "Multi-plane Scrape": "MULTIPLANE_SCRAPE",
    "Pinch/Magnify": "PINCH",
    "Grab": "GRAB",
    "Elastic Deform": "ELASTIC_DEFORM",
    "Pose": "POSE",
    "Cloth": "CLOTH",
    "Mask": "MASK",
    "Draw Face Sets": "DRAW_FACE_SETS",
}

_SCULPT_ASSET_LIBRARY_PATH = "brushes/essentials_brushes-mesh_sculpt.blend/Brush/"

_SCULPT_TOOL_NAME_TO_ASSET_NAME = {
    "Draw": "Draw",
    "Draw Sharp": "Draw Sharp",
    "Clay": "Clay",
    "Clay Strips": "Clay Strips",
    "Clay Thumb": "Clay Thumb",
    "Inflate": "Inflate/Deflate",
    "Crease": "Crease Sharp",
    "Scrape": "Scrape/Fill",
    "Multi-plane Scrape": "Scrape Multiplane",
    "Pinch": "Pinch/Magnify",
    "Grab": "Grab",
    "Elastic Deform": "Elastic Grab",
    "Pose": "Pose",
    "Cloth": "Grab Cloth",
    "Mask": "Mask",
    "Draw Face Sets": "Draw Face Sets",
}


def get_sculpt_brush_tool_name(brush):
    brush_type = get_sculpt_brush_type(brush)
    if not brush_type:
        return None
    return _SCULPT_BRUSH_TOOL_NAME_MAP.get(
        brush_type,
        brush_type.replace("_", " ").title(),
    )


def get_sculpt_brush_tool_idname(brush):
    tool_name = get_sculpt_brush_tool_name(brush)
    if not tool_name:
        return None
    return "builtin_brush." + tool_name


def get_sculpt_asset_name_from_tool_name(tool_name):
    if not tool_name:
        return None
    if tool_name in _SCULPT_TOOL_NAME_TO_ASSET_NAME:
        return _SCULPT_TOOL_NAME_TO_ASSET_NAME[tool_name]
    return tool_name


def get_sculpt_brush_asset_identifier_from_tool_name(tool_name):
    asset_name = get_sculpt_asset_name_from_tool_name(tool_name)
    if not asset_name:
        return None
    return _SCULPT_ASSET_LIBRARY_PATH + asset_name


def get_sculpt_brush_asset_identifier(brush):
    brush_name = getattr(brush, "name", None)
    if brush_name:
        normalized_name = brush_name.removeprefix("SW | ").strip()
        asset_identifier = get_sculpt_brush_asset_identifier_from_tool_name(normalized_name)
        if asset_identifier:
            return asset_identifier
    tool_name = get_sculpt_brush_tool_name(brush)
    return get_sculpt_brush_asset_identifier_from_tool_name(tool_name)


def get_legacy_sculpt_tool_idname(brush_name):
    brush_type = _LEGACY_BRUSH_NAME_TO_TYPE.get(brush_name)
    if not brush_type:
        return None
    tool_name = _SCULPT_BRUSH_TOOL_NAME_MAP.get(
        brush_type,
        brush_type.replace("_", " ").title(),
    )
    return "builtin_brush." + tool_name


def activate_sculpt_brush(context, brush):
    asset_identifier = get_sculpt_brush_asset_identifier(brush)
    if asset_identifier:
        try:
            import bpy
            result = bpy.ops.brush.asset_activate(
                asset_library_type='ESSENTIALS',
                relative_asset_identifier=asset_identifier,
            )
            if 'FINISHED' in result:
                return True
        except Exception:
            pass

    brush_type = get_sculpt_brush_type(brush)
    if brush_type:
        try:
            import bpy
            result = bpy.ops.wm.tool_set_by_brush_type(brush_type=brush_type, space_type='VIEW_3D')
            if 'FINISHED' in result:
                return True
        except Exception:
            pass

    tool_idname = get_sculpt_brush_tool_idname(brush)
    if tool_idname:
        try:
            import bpy
            result = bpy.ops.wm.tool_set_by_id(name=tool_idname)
            if 'FINISHED' in result:
                return True
        except Exception:
            pass

    try:
        context.tool_settings.sculpt.brush = brush
        return True
    except Exception:
        return False


def activate_sculpt_asset_identifier(asset_identifier):
    if not asset_identifier:
        return False
    try:
        import bpy
        result = bpy.ops.brush.asset_activate(
            asset_library_type='ESSENTIALS',
            relative_asset_identifier=asset_identifier,
        )
        return 'FINISHED' in result
    except Exception:
        return False


def get_active_sculpt_brush_asset_identifier(context):
    sculpt_settings = getattr(getattr(context, "tool_settings", None), "sculpt", None)
    if sculpt_settings is None:
        return None
    asset_ref = getattr(sculpt_settings, "brush_asset_reference", None)
    if asset_ref is None:
        return None
    return getattr(asset_ref, "relative_asset_identifier", None)


def activate_sculpt_tool_name(context, tool_name):
    asset_identifier = get_sculpt_brush_asset_identifier_from_tool_name(tool_name)
    if asset_identifier:
        try:
            import bpy
            result = bpy.ops.brush.asset_activate(
                asset_library_type='ESSENTIALS',
                relative_asset_identifier=asset_identifier,
            )
            if 'FINISHED' in result:
                return True
        except Exception:
            pass

    brush_type = _LEGACY_BRUSH_NAME_TO_TYPE.get(tool_name, tool_name.upper().replace(" ", "_").replace("-", "_"))
    try:
        import bpy
        result = bpy.ops.wm.tool_set_by_brush_type(brush_type=brush_type, space_type='VIEW_3D')
        if 'FINISHED' in result:
            return True
    except Exception:
        pass

    try:
        import bpy
        result = bpy.ops.wm.tool_set_by_id(name="builtin_brush." + tool_name)
        if 'FINISHED' in result:
            return True
    except Exception:
        pass

    return False


def find_compatible_sculpt_brush(brush_name, brushes):
    brush = brushes.get(brush_name, None)
    if brush is not None:
        return brush

    target_type = _LEGACY_BRUSH_NAME_TO_TYPE.get(brush_name)
    if not target_type:
        return None

    for brush in brushes:
        if get_sculpt_brush_type(brush) == target_type:
            return brush

    return None


def get_tool_idname_name(idname):
    if not idname or "." not in idname:
        return idname
    return idname.split(".", 1)[1]


def is_brush_tool_idname(idname):
    return idname in {"builtin.brush", "builtin_brush.brush"}


def get_unified_paint_settings(context):
    tool_settings = getattr(context, "tool_settings", None)
    if tool_settings is None:
        return None

    candidates = (
        tool_settings,
        getattr(tool_settings, "sculpt", None),
        getattr(tool_settings, "image_paint", None),
        getattr(tool_settings, "vertex_paint", None),
        getattr(tool_settings, "weight_paint", None),
        getattr(tool_settings, "gpencil_paint", None),
        getattr(tool_settings, "gpencil_vertex_paint", None),
        getattr(tool_settings, "gpencil_weight_paint", None),
    )

    for candidate in candidates:
        if candidate is None:
            continue
        settings = getattr(candidate, "unified_paint_settings", None)
        if settings is not None:
            return settings

    return None


def cache_brush_preview_icon(brush, asset_identifier=None):
    if brush is None:
        return None

    preview = getattr(brush, "preview", None)
    if preview is None:
        return None

    pixels = getattr(preview, "icon_pixels_float", None)
    if pixels:
        pixels = list(pixels)
        side = int((len(pixels) / 4) ** 0.5)
    else:
        pixels = getattr(preview, "icon_pixels", None)
        if not pixels:
            return None
        pixels = [value / 255.0 for value in pixels]
        side = int((len(pixels) / 4) ** 0.5)

    if side <= 0:
        return None

    expected_len = side * side * 4
    if len(pixels) < expected_len:
        return None

    preview_signature = ""
    icon_pixels = getattr(preview, "icon_pixels_float", None)
    if icon_pixels:
        sample = bytes(bytearray(max(0, min(255, int(v * 255.0))) for v in list(icon_pixels)))
        preview_signature = hashlib.sha1(sample).hexdigest() if sample else ""

    key = preview_signature or asset_identifier or get_sculpt_brush_asset_identifier(brush) or getattr(brush, "name", "brush")
    filename = hashlib.sha1(key.encode("utf-8")).hexdigest() + ".png"

    import bpy
    root = getattr(bpy.app, "tempdir", None) or tempfile.gettempdir()
    cache_dir = os.path.join(root, "sculpt_paint_wheel_asset_icons")
    os.makedirs(cache_dir, exist_ok=True)
    filepath = os.path.join(cache_dir, filename)

    if os.path.isfile(filepath):
        return filepath

    image_name = ".spw_icon_cache_" + filename[:-4]
    image = bpy.data.images.new(image_name, width=side, height=side, alpha=True)
    try:
        image.pixels = pixels[:expected_len]
        image.filepath_raw = filepath
        image.file_format = 'PNG'
        image.save()
    finally:
        bpy.data.images.remove(image)

    return filepath
