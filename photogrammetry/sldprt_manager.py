import re


class EquationsFile:

    def __init__(self, sync_path, keys=['VH', 'VW', 'VR'], defaults=100, units="cm"):
        self.vdict = {key:defaults for key in keys}
        self.keys = keys
        
        self.sync_path = sync_path
        self.units = units

    def parseline(self, l: str):
        val = l.split("= ")[-1]
        val = val.split(" ")
        #print(val)
        val = val[0]
        val = val.replace(self.units, "")

        return float(val)

    def load(self):
        f  = open(self.sync_path, "r").read()
        lines = f.split("\n")
        for key in self.keys:
            
            true_line = None
            for line in lines:
                if key in line:
                    true_line = line
                    break
                    
            val = self.parseline(true_line)
            self.vdict[key] = val
    
    def register(self, d):
        pass
    
    def render(self, new):
        text = f"""
"VH" = {new['VH']+26}cm

"VR"= {new['VR']}cm

"VW"= {new["VW"]}cm

"D1@Boss-Extrude3"= "VH"

"D3@Sketch3"= "VR"

"D4@Sketch3"= "VW"
            """
        
        with open(self.sync_path, "w") as f:
            f.flush()
            f.write(text)


            
def render_coral_rig(eq_path, height, left, right):
    pass

if __name__ == "__main__":
    eq = EquationsFile("photogrammetry\\equations_coral.txt")
    #eq.load()
    eq.render({"VH":22,
               "VR":45,
               "VW":35})