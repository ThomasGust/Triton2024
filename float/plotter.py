import matplotlib.pyplot as plt
#import pickle
import os
import json
import pandas as pd

LOG_INDEX = -1

def plot_log():
    #fnames = os.listdir("float\\logs")
    #name = os.path.join("float\\logs", fnames[LOG_INDEX])
    name = "log.json"
    existing = len(os.listdir("float\\figures"))

    dir_path = os.path.join("float\\figures", str(existing))
    os.mkdir(dir_path)
    
    with open(os.path.join(name), "r") as f:
        df = pd.read_json(f)
    
    dives = df['dive'].unique().tolist()

    for i, dive in enumerate(dives):
        
        data = df[df['dive']==dive]

        #Pressure over time
        plt.plot(data['float_time'], data['pressure']/1013)
        plt.title(f"Float Pressure Data, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Pressure (atm)")
        plt.savefig(os.path.join(dir_path, f"pressure_time_{dive}.png"))
        plt.close()

        #Depth over time
        plt.plot(data['float_time'], data['depth'])
        plt.title(f"Float Depth Over Time, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Depth (meters)")
        plt.savefig(os.path.join(dir_path, f"depth_time_{dive}.png"))
        plt.close()

        #Temperature over depth
        plt.plot(data['depth'], data['temperature'])
        plt.title(f"Float Temperature Over Depth, Dive {i}")
        plt.xlabel("Depth (meters)")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"depth_temperature_{dive}.png"))
        plt.close()

if __name__ == "__main__":
    plot_log()