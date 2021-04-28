_C='color'
_B='pos'
_A='co'
_I='image'
from gpu_extras.presets import *
from gpu_extras.batch import batch_for_shader as bat
from bgl import *
from .gpu_shaders import ShaderType as SType,Shader2D,SH,Shader3D,ShaderGeom as SGeom
from .gl_fun import *

#from .state import * # NEW API GIVE WRONG RESULTS LMAO...
def DiPLight(_c,_r,_co,s=SH.PLIGHT()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);b.draw(s);RstPointBlend()
def DiCFS(_c,_r,_co,s=SH.CFS()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);b.draw(s);RstPointBlend()
def DiCFSs(_r,_co,_cs):s=SH.CFS();SetPointBlend(_r*2);b=bat(s,SType.POINTS(),{'p':_cs});s.bind();s.uniform_float(_A,_co);b.draw(s);RstPointBlend()
def DiCLS(_c,_r,_seg,_lt,_co):SetLineSBlend(_lt);draw_circle_2d(_c,_co,_r,_seg);RstLineSBlend()
def DiCLSs(_r,_seg,_lt,_co,_cs):
 SetLineSBlend(_lt)
 for c in _cs:draw_circle_2d(c,_co,_r,_seg)
 RstLineSBlend()
def DiCFCL(_c,_r,_co,_lco):DiCFS(_c,_r,_co);DiCLS(_c,_r,32,2,_lco)
def DiCFCLs(_r,_co,_lco,_cs):DiCFSs(_r,_co,_cs);DiCLSs(_r,32,2,_lco,_cs)
def DiIMGA(_p,_s,_i,s=SH.IMGA()):b=bat(s,SType.TRIFAN(),SGeom.IMG(_p,_s));glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,_i);s.bind();s.uniform_int(_I, 0);SetBlend();b.draw(s);RstBlend()
def DiIMGAMMA(_p,_s,_i,s=SH.IMGA_GAMMA()):DiIMGA(_p,_s,_i,s)
def DiIMGAMMA_OP(_p,_s,_o,_i,s=SH.IMGA_GAMMA_OP()):b=bat(s,SType.TRIFAN(),SGeom.IMG(_p,_s));glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,_i);s.bind();s.uniform_float('o',_o);s.uniform_int(_I, 0);SetBlend();b.draw(s);RstBlend()
def DiL(_p1,_p2,_color=(0,0,0,0.8),s=Shader2D.UNIFORM()):b=bat(s,SType.LINES(),{_B:[_p1,_p2]});s.bind();s.uniform_float(_C,_color);SetBlend();b.draw(s);RstBlend()
shLs=Shader2D.UNIFORM()
def DiLs(_color=(0,0,0,0.8),*_points):b=bat(shLs,SType.LINES(),{_B:list(_points)});shLs.bind();shLs.uniform_float(_C,_color);SetBlend();b.draw(shLs);RstBlend()
def DiLs_(_color=(0,0,0,0.8),*_points):b=bat(shLs,SType.LINES(),{_B:_points});shLs.bind();shLs.uniform_float(_C,_color);SetBlend();b.draw(shLs);RstBlend()
def DiRNGS_SPLITANG(_c,_r,_e1,_e2,_f,_n,_act,_co,s=SH.RNGS_SPLITANG()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);s.uniform_float('e1',_e1);s.uniform_float('e2',_e2);s.uniform_float('f',_f);s.uniform_float('n',_n);s.uniform_int('act',_act);b.draw(s);RstPointBlend()
def DiRNGBLR(_c,_r,_t,_f,_co,s=SH.RNGBLR()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);s.uniform_float('t',_t);s.uniform_float('f',_f);b.draw(s);RstPointBlend()
def DiRNGBLRSLC(_c,_r,_t,_m,_co,s=SH.RNGBLRSLC()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);s.uniform_float('t',_t);s.uniform_float('mask',_m);b.draw(s);RstPointBlend()
def DiIMGA_Intensify(_p,_s,_i,_boost,s=SH.IMGA_GAMMA_INTENSIFY()):b=bat(s,SType.TRIFAN(),SGeom.IMG(_p,_s));glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,_i);s.bind();s.uniform_float('boost',_boost);SetBlend();b.draw(s);RstBlend()
def DiANILLOTONO(_c,_r,_s,_v,s=SH.RGCROMASLIN()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float("s",_s);s.uniform_float("v",_v);b.draw(s);RstPointBlend()
def DiPKCO(_c,_r,_h,s=SH.RTCROMASLIN()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(), SGeom.CIR(_c));s.bind();s.uniform_float("h",_h);b.draw(s);RstPointBlend()
def DiANILLOW(_c,_r,s=SH.RNGCROMALINW()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));b.draw(s);RstPointBlend()
def DiCFSTOP(_c,_r,_co,s=SH.CFS_CROPTOP()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);b.draw(s);RstPointBlend()
def DiCFSBOT(_c,_r,_co,s=SH.CFS_CROPBOT()):SetPointBlend(_r*2);b=bat(s,SType.POINTS(),SGeom.CIR(_c));s.bind();s.uniform_float(_A,_co);b.draw(s);RstPointBlend()