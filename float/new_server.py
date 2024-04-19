import bluetooth
import json
import threading
import time
import sys
import subprocess
import pickle as pkl
import socket
import os
import errno
import signal
import functools

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

target_name = "raspberrypi"
target_address = "B8:27:EB:A2:69:06"
is_profiling = False


def find_float_device():
    global target_address
    nearby_devices = bluetooth.discover_devices()
    for bdaddr in nearby_devices:
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
                # Example command to send
                command = input("Command: ")
                if command == "":
                    command = "s"
                self.sock.send(json.dumps({"command": command}))
                if command == "k":
                    sys.exit()
                if command == "p":
                    time.sleep(90)
                else:
                    time.sleep(1)

class DataThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        #kill_process_on_port(self.port)

        #self.sock.bind(("", self.port))
        #self.sock.listen(1)

    def connect(self):
        print("BEGINNING BSOCKET CREATION FOR data")
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.settimeout(9999)
        #self.sock.settimeout(999999)

        self.sock.connect((target_address, self.port))
        print("FINISHED SOCKT CREATION FOR DATA")
    
    def shutdown(self):
        print("Attempting Data Socket Shutdown")
        #self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Completed DataSocket Shutdown")

    def run(self):
        while True:

            self.connect()
            while not is_profiling:
                print(is_profiling)
                print("WAITING FOR DATA")
                try:
                    data = self.recvall()
                except TimeoutError or OSError:
                    data = None
                #print(data)
                print("DATA RECEIVED")
                if data == None:
                    data = pkl.load(open('log.pkl', "rb"))
                pkl.dump(data, open("log.pkl", "wb"))
            #self.shutdown()
    
    @timeout_decorator(10)
    def recvall(self):
        #If there is a cutoff in the middle of the transmission, we will need to kill this thing
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

if __name__ == "__main__":
    #if find_float_device():
    print(f"Found target bluetooth device with address {target_address}")
    
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