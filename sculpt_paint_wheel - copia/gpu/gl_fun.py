from bgl import *


def SetPoint(ps):glPointSize(ps)
def RstPoint():SetPoint(4.0)
def SetPointBlend(ps):SetPoint(ps);SetBlend()
def RstPointBlend():RstPoint();RstBlend()
def SetLine(lt):glLineWidth(lt)
def RstLine():SetLine(1.0)
def SetLineSmooth():glEnable(GL_LINE_SMOOTH)
def SetLineSBlend(lt):SetBlend();SetLineSmooth();SetLine(lt)
def RstLineSmooth():glDisable(GL_LINE_SMOOTH)
def RstLineSBlend():RstBlend();RstLineSmooth();RstLine()
def SetBlend():glEnable(GL_BLEND)
def RstBlend():glDisable(GL_BLEND)
def SetDepth():glEnable(GL_DEPTH_TEST)
def RstDepth():glDisable(GL_DEPTH_TEST)

def SetSRGB():glEnable(GL_FRAMEBUFFER_SRGB)
def RstColorSpace():glDisable(GL_FRAMEBUFFER_SRGB)
def SetBFuncAlphaZero():glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ZERO);glBlendEquation(GL_FUNC_ADD)
def SetBFuncOneAlpha():glEnable(GL_BLEND);glBlendFunc(GL_ONE,GL_ONE_MINUS_SRC_ALPHA);glBlendEquation(GL_FUNC_ADD)
def SetBFuncAlphaAlpha():glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);glBlendEquation(GL_FUNC_ADD)
def SetDefCoSpace():glEnable(GL_FRAMEBUFFER_DEFAULT)
def SetBlendAlpha():SetBlend();glBlendFunc(GL_ONE,GL_ONE_MINUS_SRC_ALPHA)

def SetScissor(xi,xf,yi,yf):glEnable(GL_SCISSOR_TEST);glScissor(int(xi),int(xf),int(yi),int(yf))
def RstScissor():glDisable(GL_SCISSOR_TEST)
def SetMultisample():glEnable(GL_MULTISAMPLE)
