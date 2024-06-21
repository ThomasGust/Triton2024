import matplotlib.pyplot as plt

if __name__ == "__main__":
    receiver1 = input("Receiver 1: ")
    receiver2 = input("Receiver 2: ")
    receiver3 = input("Receiver 3: ")

    receiver1 = [int(x) for x in receiver1.replace(" ", "").split(",")]
    receiver2 = [int(x) for x in receiver2.replace(" ", "").split(",")]
    receiver3 = [int(x) for x in receiver3.replace(" ", "").split(",")]

    print(receiver1)
    print(receiver2)
    print(receiver3)
    days = range(len(receiver1))

    plt.plot(days, receiver1, label = "Receiver 1")
    plt.plot(days, receiver2, label = "Receiver 2")
    plt.plot(days, receiver3, label = "Receiver 3")

    plt.xlabel("Day")
    plt.ylabel("# Of Sturgeon")
    plt.title("Number of Sturgeon Detected At Each Receiver Over Time")
    plt.legend()
    
    plt.savefig("sturgeon.png")
    plt.show()

"""
3, 3, 0, 0, 1, 1, 1, 1, 3, 2, 0, 2, 3, 2, 0
4, 3, 8, 8, 13, 10, 8, 4, 3, 1, 2, 1, 0, 1, 2
3, 2, 5, 6, 3, 2, 3, 3, 2, 2, 3, 2, 1, 0, 1 

"""