import matplotlib.pyplot as plt
import pickle
import os
import pandas as pd

LOG_INDEX = -1

def plot_log():
    fnames = os.listdir("float\\logs")
    name = os.path.join("float\\logs", fnames[LOG_INDEX])

    with open(os.path.join(name), "rb") as f:
        data = pickle.load(f)
        df = pd.DataFrame.from_dict(data)

    plt.plot(df['float_time'], df['mb']/1013)
    plt.title("Float Pressure Data")
    plt.xlabel("Time since recording was started (seconds)")
    plt.ylabel("Pressure (atm)")
    plt.savefig(f"float\\figures\\{fnames[LOG_INDEX]}_pressure.png")
    plt.close()

if __name__ == "__main__":
    plot_log()