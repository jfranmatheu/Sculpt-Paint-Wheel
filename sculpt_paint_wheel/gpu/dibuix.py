_C='color'
_B='pos'
_A='co'
_I='image'
from sys import platform
is_mac = platform == 'darwin'
from gpu_extras.presets import *
from gpu_extras.batch import batch_for_shader as bat
from .gpu_shaders import ShaderType as SType,BuiltinShader as Shader2D,SH,Shader3D,ShaderGeom as SGeom
from . state import *
shLs=Shader2D.UNIFORM()
def DiPLight(_c,_r,_co,s=SH.PLIGHT()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiCFS(_c,_r,_co,s=SH.CFS()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiCFSs(_r,_co,_cs):s=SH.CFS();b=bat(s,SType.POINTS(),{'p':_cs});s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiCFSGAMMA(_c,_r,_co,s=SH.CFS_GAMMA()):DiCFS(_c,_r,_co,s)
def DiCFSGAMMAs(_r,_co,_cs):s=SH.CFS_GAMMA();b=bat(s,SType.POINTS(),{'p':_cs});s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiCLS(_c,_r,_seg,_lt,_co):SetLine(_lt);draw_circle_2d(_c,_co,_r,segments=_seg);RstLine()
def DiCLSs(_r,_seg,_lt,_co,_cs):
 SetLine(_lt)
 for c in _cs:draw_circle_2d(c,_co,_r,segments=_seg)
 RstLine()
def DiCFCL(_c,_r,_co,_lco):DiCFS(_c,_r,_co);DiCLS(_c,_r,32,2,_lco)
def DiCFCLs(_r,_co,_lco,_cs):DiCFSs(_r,_co,_cs);DiCLSs(_r,32,2,_lco,_cs)
def DiIMGA(_p,_s,_i,s=SH.IMGA()):b=bat(s,SType.TRIS(),SGeom.IMG(_p,_s),indices=((0,1,2),(2,3,0)));s.bind();s.uniform_sampler('image',_i);b.draw(s)
def DiIMGAMMA(_p,_s,_i,s=SH.IMGA_GAMMA()):DiIMGA(_p,_s,_i,s) # ((0, 1), (0, 0), (1, 0), (1, 1))
def DiIMGAMMA_OP(_p,_s,_o,_i,s=SH.IMGA_GAMMA_OP()):b=bat(s,SType.TRIS(),SGeom.IMG(_p,_s),indices=((0,1,2),(2,3,0)));s.bind();s.uniform_float('o',_o);s.uniform_sampler('image',_i);b.draw(s)
def DiL(_p1,_p2,_color=(0,0,0,0.8),_lt=1.0,s=shLs):b=bat(s,SType.LINES(),{_B:[_p1,_p2]});s.bind();s.uniform_float(_C,_color);SetLine(_lt);b.draw(s);RstLine()
def DiLs(_color=(0,0,0,0.8),*_points):b=bat(shLs,SType.LINES(),{_B:list(_points)});shLs.bind();shLs.uniform_float(_C,_color);b.draw(shLs)
def DiLs_(_color=(0,0,0,0.8),*_points):b=bat(shLs,SType.LINES(),{_B:_points});shLs.bind();shLs.uniform_float(_C,_color);b.draw(shLs)
def DiRNGS_SPLITANG(_c,_r,_e1,_e2,_f,_n,_act,_co,s=SH.RNGS_SPLITANG()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);s.uniform_float('e1',_e1);s.uniform_float('e2',_e2);s.uniform_float('f',_f);s.uniform_float('n',_n);s.uniform_int('act',_act);b.draw(s);RstPoint()
def DiRNGBLR(_c,_r,_t,_f,_co,s=SH.RNGBLR()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);s.uniform_float('t',_t);s.uniform_float('f',_f);b.draw(s);RstPoint()
def DiRNGBLRSLC(_c,_r,_t,_m,_co,s=SH.RNGBLRSLC()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);s.uniform_float('t',_t);s.uniform_float('mask',_m);b.draw(s);RstPoint()
def DiIMGA_Intensify(_p,_s,_i,_boost,s=SH.IMGA_GAMMA_INTENSIFY()):b=bat(s,SType.TRIS(),SGeom.IMG(_p,_s),indices=((0,1,2),(2,3,0)));s.bind();s.uniform_sampler('image',_i);s.uniform_float('boost',_boost);b.draw(s)
def DiANILLOTONO(_c,_r,_s,_v,s=SH.RGCROMASLIN()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float("s",_s);s.uniform_float("v",_v);b.draw(s);RstPoint()
def DiPKCO(_c,_r,_h,s=SH.RTCROMASLIN()):b=bat(s,SType.POINTS(), SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float("h",_h);b.draw(s);RstPoint()
def DiANILLOW(_c,_r,s=SH.RNGCROMALINW()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));SetPoint(s,_r,False);b.draw(s);RstPoint()
def DiCFSTOP(_c,_r,_co,s=SH.CFS_CROPTOP()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiCFSBOT(_c,_r,_co,s=SH.CFS_CROPBOT()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);b.draw(s);RstPoint()
def DiRNGBLRANG(_c,_r,_t,_f,_co,_ang1,_ang2,s=SH.RNGBLRANG()):b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();SetPoint(s,_r);s.uniform_float(_A,_co);s.uniform_float('t',_t);s.uniform_float('f',_f);s.uniform_float('ang1',_ang1);s.uniform_float('ang2',_ang2);b.draw(s);RstPoint()