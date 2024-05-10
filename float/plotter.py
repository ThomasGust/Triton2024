import matplotlib.pyplot as plt
#import pickle
import os
import json
import pandas as pd

LOG_INDEX = -1

def plot_log():
    #fnames = os.listdir("float\\logs")
    #name = os.path.join("float\\logs", fnames[LOG_INDEX])
    name = os.path.join("float\\logs", os.listdir('float\\logs')[-1])
    existing = len(os.listdir("float\\figures"))

    dir_path = os.path.join("float\\figures", str(existing))
    os.mkdir(dir_path)
    
    with open(os.path.join(name), "r") as f:
        df = pd.read_json(f)
        df = df[1:]
    
    st = df.iloc[0]['float_time']

    dives = df['dive'].unique().tolist()

    for i, dive in enumerate(dives):
        
        data = df[df['dive']==dive]
        time = [t-st for t in list(data['float_time'])]

        i+=1
        #Pressure over time
        plt.plot(time, data['pressure']/1013)
        plt.title(f"Float Pressure Data, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Pressure (atm)")
        plt.savefig(os.path.join(dir_path, f"pressure_time_{dive}.png"))
        plt.close()

        #Depth over time
        p = plt.plot(time, data['depth'])
        plt.ylim(max(data['depth']), min(data['depth']))
        plt.title(f"Float Depth Over Time, Dive {i}")
        plt.xlabel("Time since recording was started (seconds)")
        plt.ylabel("Depth (meters)")
        plt.savefig(os.path.join(dir_path, f"depth_time_{dive}.png"))
        plt.close()

        #Temperature over depth
        plt.plot(time, data['temperature'])
        plt.title(f"Float Temperature Over Depth, Dive {i}")
        plt.xlabel("Depth (meters)")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"depth_temperature_{dive}.png"))
        plt.close()

        #Temperature over time
        plt.plot(time, data['temperature'])
        plt.title(f"Float Temperature Over Time, Dive {i}")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"temperature_time_{dive}.png"))
        plt.close()

        #Temperature over time
        plt.plot(range(len(data['float_time'])), data['temperature'])
        plt.title(f"Float Temperature Over Sensor Polls {i}")
        plt.xlabel("Sensor Polls")
        plt.ylabel("Temperature (C)")
        plt.savefig(os.path.join(dir_path, f"temperature_polls_{dive}.png"))
        plt.close()

def compute_first_derivative():
    with open(os.path.join("log.json"), "r") as f:
        df = pd.read_json(f)
        df = df[1:]
    
    times = list(df['float_time'])
    depths = list(df['depth'])

    velocities = [(depths[i+1]-depths[i])/(times[i+1]-times[i]) for i in range(len(times)-1)]

    plt.plot(times[1:], velocities)
    plt.savefig("velocity.png")


if __name__ == "__main__":
    plot_log()