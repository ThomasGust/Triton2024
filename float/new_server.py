import bluetooth
import json
import threading
import time
import sys
import subprocess
import pickle as pkl
import json
import functools
import os

class TimeoutError(Exception):
    pass

def timeout_decorator(timeout):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError("Function call timed out")]
            def function_thread(result_list):
                try:
                    result_list[0] = func(*args, **kwargs)
                except Exception as e:
                    result_list[0] = e

            thread = threading.Thread(target=function_thread, args=(result,))
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                thread.join() # Ensure thread releases resources, might want to handle this differently.
                raise TimeoutError("Function call timed out")

            if isinstance(result[0], Exception):
                raise result[0]

            return result[0]
        return wrapper
    return decorator

target_name = "triton"
#target_address = "B8:27:EB:D2:70:92"
target_address = "00:1A:7D:DA:71:13"
is_profiling = False


def find_float_device():
    global target_address
    nearby_devices = bluetooth.discover_devices()
    for bdaddr in nearby_devices:
        print(nearby_devices)
        if target_name == bluetooth.lookup_name(bdaddr):
            target_address = bdaddr
            return True
    return False

def kill_process_on_port(port):
    try:
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            subprocess.check_call(["fuser", "-k", f"{port}/tcp"])
        elif sys.platform == 'win32':
            result = subprocess.check_output(f"netstat -aon | findstr :{port}", shell=True)
            lines = result.decode().strip().split('\n')
            for line in lines:
                parts = line.strip().split()
                pid = parts[-1]
                subprocess.check_call(["taskkill", "/F", "/PID", pid])
        else:
            print(f"Unsupported OS: {sys.platform}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill process on port {port}: {e}")


class CommandThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def connect(self):
        print("BEGINNING BSOCKET CREATION FOR CMD")
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(9999)
        #self.sock.settimeout(999999)

        self.sock.connect((target_address, self.port))
        print("FINISHED SOCKT CREATION FOR COMMND")
    
    def shutdown(self):
        print("Attempting Command Socket Shutdown")
        self.sock.close()
        print("Completed Command Socket Shutdown")

    def run(self):
        global is_profiling

        while True:
            self.connect()
            while True:
                """c: Dumb, time based profile
                   p: Configureable depth and velocity based profile
                   y: Command, wait chain
                """
                # Example command to send
                usr = input("Command, Params: ")
                usr = usr.split(",")

                command, params = usr[0], usr[1]
                params = params.replace(" ", "")
                params = json.load(open(params, "r"))


                if command == "":
                    command = "s"

                self.sock.send(json.dumps({"command": command, "params":params}))

                if command == "k":
                    sys.exit()
                else:
                    time.sleep(1)

class DataThread(threading.Thread):
    """
    A class representing a thread for handling data communication.

    Args:
        port (int): The port number to connect to.

    Attributes:
        port (int): The port number to connect to.
        sock (bluetooth.BluetoothSocket): The Bluetooth socket for data communication.

    Methods:
        connect(): Connects to the target address on the specified port.
        shutdown(): Shuts down the data socket.
        run(): The main execution logic of the thread.
        recvall(): Receives data from the socket until a specific end marker is found.
    """

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

        current_logs = os.listdir("float\\logs")
        num_logs = len(current_logs)
        self.log_name = f"float\\logs\\log_{num_logs}.json"

    def connect(self):
        """
        Connects to the target address on the specified port.
        """
        print("BEGINNING BSOCKET CREATION FOR data")
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(9999)
        self.sock.connect((target_address, self.port))
        print("FINISHED SOCKT CREATION FOR DATA")
    
    def shutdown(self):
        """
        Shuts down the data socket.
        """
        print("Attempting Data Socket Shutdown")
        self.sock.close()
        print("Completed DataSocket Shutdown")

    def run(self):
        """
        The main execution logic of the thread.
        """
        while True:
            self.connect()
            while not is_profiling:
                current_data = json.load(open("float\\logs\\log_86.json", "r"))  
                try:
                    data = self.recvall()
                except TimeoutError or OSError as e:
                    print("ERROR", e)
                    data = None
                if data == None:
                    data = json.load(open(self.log_name, "r"))  
                
                #Match up current data with new data using i field
                current_is = [d["i"] for d in current_data]
                new_is = [d["i"] for d in data]

                data_dict = {}
                for i in range(len(data)):
                    data_dict[data[i]["i"]] = data[i]

                for i in new_is:
                    if i not in current_is:
                        current_data.append(data_dict[i])

                print(data[-1])
                
                j = json.dumps(current_data, indent=4)
                with open(self.log_name, "w") as f:
                    f.write(j)
    
    @timeout_decorator(10)
    def recvall(self):
        """
        Receives data from the socket until a specific end marker is found.

        Returns:
            dict: The received data as a dictionary.
        """
        finished = False
        full_data = b''
        end = "_EODT_:!:_EODT_"
        byte_end = end.encode('utf-8')
        while not finished:
            data = self.sock.recv(1024)
            full_data += data
            finished = byte_end in full_data
        
        deserialized = str(full_data, encoding='utf-8')
        j = deserialized.split(end)[0]
        j = json.loads(j)

        return j
#1657 E Stone Drive STEB Kingsport Tennessee 37660 423-765-2679
if __name__ == "__main__":
    #if find_float_device():
    #find_float_device()
    
    command_thread = CommandThread(5)
    data_thread = DataThread(6)
    command_thread.start()
    data_thread.start()
    command_thread.join()
    data_thread.join()
    """
    else:
       print("Could not find target bluetooth device.")
    """