_A=None
try:from bl_math import *
except:from .fun import clamp,smoothstep,lerp
from enum import Enum
from time import time as get_time
class EaseLinear:
	def __call__(self,v1,v2,t):return lerp(v1,v2,t)
class EaseVectorLinear:
	def __call__(self,v1,v2,t):return lerp(v1[0],v2[0],t),lerp(v1[1],v2[1],t)
class EaseSmooth:
	def __call__(self,v1,v2,t):return smoothstep(v1,v2,t)
class EaseVectorSmooth:
	def __call__(self,v1,v2,t):return smoothstep(v1[0],v2[0],t),smoothstep(v1[1],v2[1],t)
class Ease(Enum):
	LINEAR=EaseLinear;SMOOTH=EaseSmooth;VECTOR_LINEAR=EaseVectorLinear;VECTOR_SMOOTH=EaseVectorSmooth
	def __call__(self):return self.value()
class Anim:
	def __init__(self,data,attr,destination,time):
		B='ERROR';A='#';self.data=data
		if A in attr:
			self.attr,self.index=attr.split(A);self.index=int(self.index);start=getattr(data,self.attr,_A)
			if not start:print(B);return None
			self.start=start[self.index]
		else:
			self.attr=attr;self.index=-1;self.start=getattr(data,self.attr,_A)
			if not self.start:print(B);return None
		self.end=destination;self.start_time=get_time();self.time=time;self.ease=EaseLinear()if type(self.start)==float else EaseVectorLinear()
	def set_ease(self,ease=EaseSmooth):
		if hasattr(self,ease):del self.ease
		if isinstance(ease,Ease):self.ease=ease()
		else:self.ease=ease
		return self
	def set_delay(self,delay):self.delay=delay;return self
	def set_on_end(self,callback,*args,**kwargs):self.end_callback=callback;self.end_args=args if args and args[0]else _A;self.end_kwargs=kwargs
	def __call__(self):
		t=(get_time()-self.start_time)/self.time
		if clamp(t,0,1)==1:self.update(self.end);self.on_end();return False
		self.update(self.ease(self.start,self.end,t));return True
	def update(self,value):
		if self.index!=-1:attr=getattr(self.data,self.attr);attr[self.index]=value;setattr(self.data,self.attr,attr)
		else:setattr(self.data,self.attr,value)
	def on_end(self):
		if not hasattr(self,'end_callback'):return
		if self.end_args:self.end_callback(*self.end_args,**self.end_kwargs)
		elif self.end_kwargs:self.end_callback(**self.end_kwargs)
		else:self.end_callback()