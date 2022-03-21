from datetime import datetime


class ToolsManagement():
    def get_active_toolset(self):
        return self.toolsets[self.active_toolset] if self.active_toolset != -1 else None

    def add_toolset(self, name):
        n = len(self.toolsets)
        if n >= 12:
            return
        new_toolset = self.toolsets.add()
        new_toolset.name = name if name != '' else 'Toolset_' + str(n)
        new_toolset.uuid = datetime.today().strftime('%Y%m%d%H%M%S') # Inverted date and time.
        self.active_toolset = n
        self.toolset_list = str(n)
        #OP.ed.undo_push(message='Added new toolset')
        return new_toolset

    def get_toolset(self, name):
        return self.toolsets.get(name, None)

    def get_toolset_index(self, name):
        i = 0
        for ts in self.toolsets:
            if ts.name == name:
                return i
            i += 1
        return -1

    def remove_toolset(self, toolset, remove_global: bool = True):
        if isinstance(toolset, int):
            if toolset == -1:
                return

            ts = self.toolsets[toolset]
            if ts.use_global and remove_global:
                from .. io.io import remove_sculpt_toolset_from_globals
                remove_sculpt_toolset_from_globals(None, ts)

            self.toolsets.remove(toolset)
            self.active_toolset = len(self.toolsets) - 1
            self.toolset_list = str(self.active_toolset) if self.active_toolset != -1 else 'NONE'

        elif isinstance(toolset, str):
            self.remove_toolset(self.get_toolset_index(toolset))