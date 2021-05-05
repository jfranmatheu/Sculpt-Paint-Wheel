from .. utils import point_inside_circle, point_inside_rect, Vector, load_image_from_filepath, clear_image
from .. gpu.dibuix import DiCFCL, DiIMGA, DiCLS, DiIMGAMMA_OP, DiIMGA_Intensify
from .. gpu.text import Draw_Text_AlignCenter
import bpy
from os.path import exists
from bpy.types import Image
from gpu.texture import from_image as gpu_texture_from_image


class Tool():
    def __init__(self, label:str, name: str, is_brush: bool = False, tool_icon: "DefToolImage" = None, flags: set = set()):
        self.label = label
        self.name = name
        self.is_brush = is_brush
        self.identifier = 'builtin_brush.' + name if is_brush else 'builtin.' + name # if brush starts with mayus else minus
        self._pos = Vector((0, 0))
        self._center = Vector((0, 0))
        self.offset = Vector((0, 0))
        self.tool_icon = tool_icon
        self.icon = None
        self.texture = None
        self.is_on_hover = False
        self.flags = flags
    
    @property
    def pos(self):
        return self._pos
    
    @property
    def center(self):
        return self._center
    
    @pos.setter
    def pos(self, value):
        self._pos = value
        #if hasattr(self, 'offset'):
        #    self._pos += self.offset
    
    @center.setter
    def center(self, value):
        self._center = value
        #if hasattr(self, 'offset'):
        #    self._center += self.offset
    
    def load_icon(self):
        # BUG: ReferenceError: StructRNA of type Image has been removed
        if self.icon and isinstance(self.icon, Image):
            self.icon.gl_load()
        else:
            icon = self.tool_icon()
            if icon:
                #icon.gl_load()
                self.icon = icon
                self.texture = gpu_texture_from_image(icon)
        '''
        if self.icon_path and exists(self.icon_path):
            icon = load_image_from_filepath(self.icon_path)
            if not icon:
                return
            icon.name = "." + icon.name
            icon.gl_load()
            self.icon = icon
        '''
    
    def unload_icon(self):
        if self.icon:
            self.icon.gl_free()
            #clear_image(self.icon)
            
            # FIX BUG: ReferenceError: StructRNA of type Image has been removed
            self.icon = None
            self.texture = None
    
    def on_hover(self, mouse, size) -> bool:
        is_on_hover = point_inside_rect(mouse, self.pos, size)
        if is_on_hover:
            if not self.is_on_hover:
                self.is_on_hover = True
                self.on_hover_enter()
        elif self.is_on_hover:
                self.is_on_hover = False
                self.on_hover_exit()
        return is_on_hover
    
    def on_hover_enter(self):
        pass
    
    def on_hover_exit(self):
        pass

    def __call__(self):
        if self.is_on_hover:
            if hasattr(self, 'operator'):
                eval(self.operator)('INVOKE_DEFAULT')
            bpy.ops.wm.tool_set_by_id(name=self.identifier)
            return True
    
    def draw(self, s, r, ts, act=False):
        if act:
            co = (.45, .65, .9, .8) if self.is_on_hover else (.3, .5, .75, .8)
        else:
            co = (.24, .24, .24, .8) if self.is_on_hover else (.1, .1, .1, .8)
        DiCFCL(self.center, r, co, (.4, .4, .4, .9))
        if self.icon:
            if self.is_on_hover:
                DiIMGA_Intensify(self.pos, s, self.texture, 1.5)
            else:
                DiIMGAMMA_OP(self.pos, s, .9, self.texture)
        else:
            Draw_Text_AlignCenter(*self.center, self.label, ts)


class Toolbar():
    def __init__(self, pos: tuple = (0, 0), item_size: int = 24, hor_align: str = 'CENTER', ver_align: str = 'TOP', direction: str = 'HORIZONTAL', rows_cols: int = 1):
        self.init_pos = Vector(pos)
        self.pos = Vector(pos)
        self.size = Vector((item_size if direction == 'HORIZONTAL' else 0, item_size if direction == 'VERTICAL' else 0))
        self.increment_size = Vector((int(direction == 'HORIZONTAL'), int(direction == 'VERTICAL')))
        self.item_size = item_size
        self.is_on_hover = False
        self.hovered_tool = None
        self.active_tool = None
        self.num_tools = 0
        self.spacing = Vector((6, 5))
        self.items_per_row_col = 1
        self.tools = {}
        self.hor_align = hor_align
        self.ver_align = ver_align
        self.direction = direction
        self.rows_cols = rows_cols
    
    def tool(self, label, name, is_brush, tool_icon, flags, kwargs = None):
        tool = Tool(label, name, is_brush, tool_icon, flags)
        if kwargs:
            for key, value in kwargs.items():
                setattr(tool, key, value)
        self.tools[name] = tool
        self.num_tools += 1
        
        from math import ceil
        self.items_per_row_col = ceil(self.num_tools/self.rows_cols)
        #self.size += (self.increment_size * self.item_size)
        #self.update_pos()
    
    def update_pos(self):
        if self.hor_align == 'LEFT':
            self.pos.x = self.init_pos.x
        elif self.hor_align == 'CENTER':
            self.pos.x = self.init_pos.x - (self.item_size * (self.items_per_row_col / 2) + self.spacing.x * ((self.items_per_row_col-1) / 2)) # self.num_tools
        elif self.hor_align == 'RIGHT':
            self.pos.x = self.init_pos.x - (self.item_size * self.items_per_row_co + self.spacing.x * (self.items_per_row_co-1)) # self.num_tools
        
        if self.ver_align == 'BOTTOM':
            self.pos.y = self.init_pos.y
        elif self.ver_align == 'MIDDLE':
            self.pos.y = self.init_pos.y - self.item_size / 2
        elif self.ver_align == 'TOP':
            self.pos.y = self.init_pos.y - self.item_size
            
        self.update_childs()
    
    def update_childs(self):
        item_rad = self.item_size/2
        item_size = Vector((self.item_size, self.item_size))
        item_size_2 = item_size / 2
        pos = self.pos.copy() + Vector((0, self.size.y - self.item_size))
        
        max_offset = Vector((0, 0))

        row_col_item_counter = 0
        for tool in self.tools.values():
            tool.pos = pos + self.increment_size * self.item_size * row_col_item_counter + tool.offset
            tool.center = tool.pos + item_size_2
            
            row_col_item_counter += 1
            
            if self.rows_cols != 1:
                if row_col_item_counter == self.items_per_row_col:
                    pos -= Vector((0, self.item_size+self.spacing.y))
                    row_col_item_counter = 0
                    pos.x = self.pos.x
                else:
                    pos.x += self.spacing.x
            else:
                pos.x += self.spacing.x
                
            max_offset.x = max(abs(max_offset.x), abs(tool.offset.x))
            max_offset.y = max(abs(max_offset.y), abs(tool.offset.y))
        
        if max_offset.x != 0 or max_offset.y != 0:
            self.pos -= max_offset
            self.size += max_offset

    
    def show(self, context, pos, item_size):
        self.init_pos = pos
        self.item_size = item_size
        self.size = Vector((item_size * self.items_per_row_col + self.spacing.x * (self.items_per_row_col-1), item_size * self.rows_cols + self.spacing.y * (self.rows_cols-1)))
        self.update_pos()
        
        idname = context.workspace.tools.from_space_view3d_mode(context.mode).idname
        t_type = idname.split('.')[1]
        
        if t_type in self.tools:
            self.active_tool = self.tools[t_type]

        for tool in self.tools.values():
            tool.load_icon()


    def on_hover(self, mouse) -> bool:
        is_on_hover = point_inside_rect(mouse, self.pos, self.size)
        if is_on_hover:
            if not self.is_on_hover:
                self.is_on_hover = True
                self.on_hover_enter()
        elif self.is_on_hover:
            self.is_on_hover = False
            self.on_hover_exit()
        return is_on_hover
    
    def on_hover_enter(self):
        pass
    
    def on_hover_exit(self):
        pass
    
    def on_hover_tool(self, mouse):
        item_size = Vector((self.item_size, self.item_size))
        for tool in self.tools.values():
            if tool.on_hover(mouse, item_size):
                if self.hovered_tool and self.hovered_tool != tool:
                    self.hovered_tool.is_on_hover = False
                self.hovered_tool = tool
                return tool
        self.hovered_tool = None
        return None
    
    def on_event(self, event, mouse) -> bool:
        if not self.on_hover(mouse):
            if self.hovered_tool:
                self.hovered_tool.is_on_hover = False
                self.hovered_tool = None
            return False
        if not self.on_hover_tool(mouse):
            return True
        if self.hovered_tool == self.active_tool and 'ALWAYS_TRIGGER' not in self.active_tool.flags:
            return True
        
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if self.hovered_tool():
                self.active_tool = self.hovered_tool
            return True
        
        return True
    
    def unload(self):
        for tool in self.tools.values():
            tool.unload_icon()
    
    def draw(self, ts):
        item_rad = self.item_size/2
        item_size = Vector((self.item_size, self.item_size))
        for tool in self.tools.values():
            tool.draw(item_size, item_rad, ts, tool==self.active_tool)
        #if self.hovered_tool:
        #    DiCLS(self.hovered_tool.center, item_rad, 32, 2.0, (0, .8, .9, 1.0))
