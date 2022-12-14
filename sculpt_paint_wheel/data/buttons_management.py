import uuid


class ButtonsManagement():
    def add_custom_button(self, data):
        n = len(self.custom_buttons)
        if n >= 10:
            return
        b = self.custom_buttons.add()
        b.id = uuid.uuid4().hex
        b.name = data.name
        b.type = data.type
        b.as_attribute = data.as_attribute
        if data.as_attribute == 'CUSTOM':
            b.custom_identifier = b.attr = data.custom_identifier
            if data.type == 'OPERATOR':
                b.attr = "import bpy\n" + b.attr
        else:
            if data.type == 'POPUP':
                b.popup_type = data.popup_type
                if data.popup_type == 'MENU':
                    b.attr = b.preset_menu = data.preset_menu
                elif data.popup_type == 'PANEL':
                    b.attr = b.preset_panel = data.preset_panel
                else:
                    b.attr = data.custom_identifier
            elif data.type == 'OPERATOR':
                b.preset_operator = data.preset_operator
                op = data.preset_operator if not data.preset_operator.startswith('_') else get_enum_desc(data, 'preset_operator')
                if '#' in op:
                    split = op.split('#')
                    op = split[0] + ('(' + split[1] + ')')
                else:
                    op += '()'
                b.attr = 'import bpy\nbpy.ops.' + op
            else:
                print("OPS! Toggles are not supported yet but one was created!")
        #print(b.attr)
        if data.image_path.startswith('//'):
            from os.path import abspath
            b.image_path = abspath(data.image_path)
        else:
            b.image_path = data.image_path
        b.index = n
        return b

    def deserialize_custom_button(self, data={}):
        if not data:
            return
        n = len(self.custom_buttons)
        if n >= 10:
            return
        b = self.custom_buttons.add()
        b.id = data['id']
        b.name = data['name']
        b.type = data['type']
        b.as_attribute = data['as_attribute']
        if data['as_attribute'] == 'CUSTOM':
            b.custom_identifier = b.attr = data['custom_identifier']
            if data['type'] == 'OPERATOR':
                b.attr = "import bpy\n" + b.attr
            elif data['type'] == 'POPUP':
                b.popup_type = data['popup_type']
        else:
            if b.type == 'POPUP':
                b.popup_type = data['popup_type']
                if b.popup_type == 'MENU':
                    b.attr = b.preset_menu = data['preset_menu']
                elif b.popup_type == 'PANEL':
                    b.attr = b.preset_panel = data['preset_panel']
                else:
                    b.attr = data['custom_identifier']
            elif b.type == 'OPERATOR':
                b.preset_operator = data['preset_operator']
                op = data['custom_identifier'] # if not data['preset_operator'].startswith('_') else get_enum_desc(data, 'preset_operator')
                if '#' in op:
                    split = op.split('#')
                    op = split[0] + ('(' + split[1] + ')')
                else:
                    op += '()'
                b.attr = 'import bpy\nbpy.ops.' + op
            else:
                print("OPS! Toggles are not supported yet but one was created!")
        #print(b.attr)
        b.image_path = data['image_path']
        b.index = n
        return b

    def remove_custom_button(self, index):
        if index >= len(self.custom_buttons):
            return
        self.custom_buttons.remove(index)
    
    def remove_all_custom_buttons(self):
        for i in range(0, len(self.custom_buttons)):
            self.custom_buttons.remove(0)

    def get_custom_button(self, button):
        if isinstance(button, int):
            return self.custom_buttons[button]
        elif isinstance(button, str):
            return self.custom_buttons.get(button, None)
        
    def call_custom_button(self, index):
        if index >= len(self.custom_buttons) or index < 0:
            return False
        self.custom_buttons[index]()
        return True

    def load_default_custom_buttons(self, def_buttons):
        while self.custom_buttons:
            self.custom_buttons.remove(0)
        for data in def_buttons:
            self.deserialize_custom_button(data)
