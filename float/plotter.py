import matplotlib.pyplot as plt
#import pickle
import os
import json
import pandas as pd
from scipy.interpolate import interp1d
import numpy as np

LOG_INDEX = -1

def plot_log():
    existing = int(len(os.listdir("float\\figures")))
    dir_path = os.path.join("float\\figures", str(existing+1))
    current_figures = os.mkdir(dir_path)

    log_dir_path = "float\\logs"
    log_name = f"log_{str(len(os.listdir(log_dir_path))-1)}.json"


    
    with open(os.path.join(log_dir_path, log_name), "r") as f:
        df = pd.read_json(f)
        print(df)
        df = df[10:]
    
    
    st = df.iloc[0]['ft']

    dives = df['dc'].unique().tolist()

    for i, dive in enumerate(dives):
        
        
        data = df[df['dc']==dive]
        time = [t-st for t in list(data['ft'])]
        depth = [d + 0.4 for d in list(data['d'])]
        #f = interp1d(data["depth"], time, kind='cubic')

        #depth_dense = np.linspace(min(data["depth"]), max(data['depth']), 300)

        i+=1
        #Pressure over time
        plt.plot(time, data['p']/1013)
        plt.title(f"Float Pressure Data, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Pressure (atm)")
        plt.savefig(os.path.join(dir_path, f"pressure_time_{dive}.png"))
        plt.close()

        #Depth over time
        p = plt.plot(time, depth)
        plt.ylim(max(depth), min(depth))
        plt.title(f"Float Depth Over Time, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Depth (meters)")
        plt.savefig(os.path.join(dir_path, f"depth_time_{dive}.png"))
        plt.close()

        #Temperature over depth
        plt.plot(time, data['t'])
        plt.title(f"Float Temperature Over Depth, Dive {i}")
        plt.xlabel("Depth (meters)")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"depth_temperature_{dive}.png"))
        plt.close()

        #Temperature over time
        plt.plot(time, data['t'])
        plt.title(f"Float Temperature Over Time, Dive {i}")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"temperature_time_{dive}.png"))
        plt.close()

        #Temperature over time
        plt.plot(range(len(data['ft'])), data['t'])
        plt.title(f"Float Temperature Over Sensor Polls {i}")
        plt.xlabel("Sensor Polls")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"temperature_polls_{dive}.png"))
        plt.close()

def compute_first_derivative():
    with open(os.path.join("log.json"), "r") as f:
        df = pd.read_json(f)
        df = df[1:]
    
    times = list(df['ft'])
    depths = list(df['d'])

    velocities = [(depths[i+1]-depths[i])/(times[i+1]-times[i]) for i in range(len(times)-1)]

    plt.plot(times[1:], velocities)
    plt.savefig("velocity.png")


if __name__ == "__main__":
    plot_log()