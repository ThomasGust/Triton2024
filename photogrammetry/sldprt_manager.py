
class EquationsFile:

    def __init__(self, sync_path, keys=['height, left, right'], defaults=100, units="cm"):
        self.vdict = {key:defaults for key in keys}
        self.keys = keys
        
        self.sync_path = sync_path
        self.units = units

    def parseline(self, l: str):
        val = l.split("= ")[-1]
        val = val.replace(self.units, "")

        return float(val)

    def load(self):
        f  = open(self.sync_path, "r").read()
        
        lines = f.split("\n")
        for key in self.keys:
            
            true_line = None
            for line in lines:
                if key in lines:
                    true_line = line
                    break
                    
            val = self.parseline(true_line)
            self.vdict[key] = val
    
    def register(self, d):
        pass
    
    def render(self):
        pass
            
def render_coral_rig(eq_path, height, left, right):
    pass