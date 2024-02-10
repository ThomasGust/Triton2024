import matplotlib.pyplot as plt
import pickle
import os

LOG_INDEX = -1

def plot_log():
    fnames = os.listdir("float\\logs")
    name = os.path.join("float\\logs", fnames[LOG_INDEX])

    with open(os.path.join(name), "rb") as f:
        data = pickle.load(f)
        print(data)

if __name__ == "__main__":
    plot_log()