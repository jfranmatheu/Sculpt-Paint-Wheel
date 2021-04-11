from math import pi, sin, asin, cos, radians, atan2, hypot, acos, sqrt
from mathutils import Vector
from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile
import bpy

images_folder = join(dirname(dirname(__file__)), 'images')


def getN_big_small_circles(R, r):
    return pi / asin(r / R)

def getr_big_small_circles(R, N):
    return sin(pi / N) * R

def getr_big_small_circles_2(N, R):
    return R * sin(pi / N) / (1 - sin(pi / N))

def getr_big_small_circles_3(R, N):
    return R * sin(pi  /N) / (1 + sin(pi / N))

def getR_big_small_circles(r, N):
    if N == 0:
        return 0
    return r / sin(pi/N)

def getPt_big_small_circles(C, P, N):
    return rotate_point_around_point(C, P, radians(360 / N))

def rotate_point_around_point(o, p, angle): # origin, point
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in rad.
    """
    #ox, oy = origin
    #px, py = point

    qx = o.x + cos(angle) * (p.x - o.x) - sin(angle) * (p.y - o.y)
    qy = o.y + sin(angle) * (p.x - o.x) + cos(angle) * (p.y - o.y)
    return Vector((qx, qy))

def get_point_in_circle_from_angle(c, r, a):
    return Vector((c.x + r * cos(a), c.y + r * sin(a)))

def smoothstep(edge0, edge1, x):
  # Scale, bias and saturate x to 0..1 range
  x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
  # Evaluate polynomial
  return x * x * (3 - 2 * x)

def clamp(x, lowerlimit, upperlimit):
  if (x < lowerlimit):
    x = lowerlimit
  if (x > upperlimit):
    x = upperlimit
  return x

def linear_interpol(x1: float, x2: float, y1: float, y2: float, x: float) -> float:
    """Perform linear interpolation for x between (x1,y1) and (x2,y2) """
    return ((y2 - y1) * x + x2 * y1 - x1 * y2) / (x2 - x1)

def lerp_point(t, times, points):
    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]
    dt = (t-times[0]) / (times[1]-times[0])
    return dt*dx + points[0][0], dt*dy + points[0][1]

# Precise method, which guarantees v = v1 when t = 1.
def lerp(v0: float, v1: float, t: float) -> float:
  return (1 - t) * v0 + t * v1

def lerp_smooth(v0: float, v1: float, t: float) -> float:
  return t*t*t*(t*(6.0*t-15.0)+10.0)

def lerp_in(v0: float, v1: float, t: float) -> float:
  return sin(t*pi*0.5)

def lerp_out(v0: float, v1: float, t: float) -> float:
  return t*t

def ease_quadratic_out(t, start, change, duration):
	t /= duration
	return -change * t*(t-2) + start

def ease_sine_in(t, b, c, d=1.0):
	return -c * cos(t/d * (pi/2)) + c + b

def v2_to_angle(_v2, _inRadians = False):
    _v2 = _v2.normalized() # must be normalized
    if _inRadians:
        return atan2(_v2.x, _v2.y)
    else:
        return atan2(_v2.x, _v2.y)*180/pi

def distance_between(_p1, _p2):
    return hypot(_p1[0] - _p2[0], _p1[1] - _p2[1])
    #return math.sqrt((_p1[1] - _p1[0])**2 + (_p2[1] - _p2[0])**2)

def direction_from_to(_p1, _p2, _norm=True):
    if _norm:
        return (_p1 - _p2).normalized()
    else:
        return _p1 - _p2

def point_inside_circle(_p, _c, _r):
    return distance_between(_p, _c) < _r

def point_inside_rect(_p, _pos, _size):
    return ((_pos[0] + _size[0]) > _p[0] > _pos[0]) and ((_pos[1] + _size[1]) > _p[1] > _pos[1])

def point_inside_ring(_p, _c, _r1, _r2):
    d = distance_between(_p, _c)
    return d > _r1 and d < _r2

def clamp(value, _min, _max):
    return min(max(value, _min), _max)

def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return sqrt(dotproduct(v, v))

def angle_between(v1, v2):
  return acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def clear_image(image):
    if not image:
        return
    image.gl_free()  # free opengl image memory
    image.buffers_free()
    image.user_clear()

def remove_image(image):
    if not image:
        return
    # delete image
    # print(image)
    bpy.data.images.remove(image, do_unlink=True, do_id_user=True, do_ui_user=True)

def load_image(image_name, ext='.png', from_path="tools"):
    path = join(images_folder, from_path, image_name+ext)
    if not isfile(path):
        print("ERROR image [%s] not found in path [%s]" % (image_name, path))
        return None
    return bpy.data.images.load(path, check_existing=True)

def load_image_from_file_dir(file, image_name, ext='.png', from_path="tools"):
    path = join(images_folder, from_path, image_name+ext)
    if not isfile(path):
        return None
    return bpy.data.images.load(path, check_existing=True)

def load_image_from_filepath(filepath):
    if not isfile(filepath):
        return None
    return bpy.data.images.load(filepath, check_existing=True)

def swap(a, b):
    temp = a
    a = b
    b = a
    return a, b
