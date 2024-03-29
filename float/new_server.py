import bluetooth
import json
import threading
import time
import sys
import subprocess
import pickle as pkl

target_name = "raspberrypi"
target_address = "B8:27:EB:A2:69:06"

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
        #kill_process_on_port(self.port)
        #self.sock.bind(("", self.port))
        #self.sock.listen(1)

    def run(self):
        while True:
            
            connected = False
            while not connected:
                try:
                    self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.sock.settimeout(999999)

                    self.sock.connect((target_address, self.port))
                    print("Accepted command connection from ", target_address)
                    connected=True
                except OSError:
                    print("OS ERROR")
                    connected=False
                    time.sleep(3)
            try:
                while True:
                    # Example command to send
                    command = input("Command: ")
                    if command == "":
                        command = "s"
                    self.sock.send(json.dumps({"command": command}))
                    if command == "k":
                        sys.exit()
                    if command == "p":
                        time.sleep(83)
                    else:
                        time.sleep(1)
            except TimeoutError or bluetooth.BluetoothError as e:
                print(e)
                self.sock.close()

class DataThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        #kill_process_on_port(self.port)

        #self.sock.bind(("", self.port))
        #self.sock.listen(1)

    def run(self):
        while True:

            connected = False
            while not connected:
                try:
                    self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                    self.sock.settimeout(999999)
                    self.sock.connect((target_address, self.port))
                    print("Accepted data connection from ", target_address)
                    connected=True
                except OSError:
                    print("OS ERROR 100")
                    connected=False
                    time.sleep(2)
            try:
                while True:
                    print("WAITING FOR DATA")
                    data = self.receive_data_in_chunks(self.sock)
                    print("DATA RECEIVED")
                    if data == None:
                        data = pkl.load(open('log.pkl', "rb"))
                    pkl.dump(data, open("log.pkl", "wb"))
           # except TimeoutError or bluetooth.BluetoothError or pkl.UnpicklingError or EOFError as e:
            except pkl.UnpicklingError or EOFError as e:
                if type(e) == type(pkl.UnpicklingError) or type(EOFError):
                    data = pkl.load(open("log.pkl", "rb"))
                    print("DATA ERROR")
                else:
                    print("CLOSING SOCKET")
                    self.sock.close()
    
    @staticmethod
    def receive_data_in_chunks(sock):
        # Receive the length of the data first
        """
        length_str = ''
        char = ''
        while char != '\n':
            char = sock.recv(1).decode('utf-8')
            length_str += char

            total_size = int(length_str)
        total_size += 1000

        # Now receive the data in chunks
        received_data = b''
        """
        received_data = b''

        truncated = True
        while truncated:
            print("STARTING RECV")
            chunk = sock.recv(2^17)
            print("END RECV")
            received_data += chunk
            #print(received_data)
            try:
                data = pkl.loads(received_data)
                truncated=False
            except pkl.UnpicklingError or EOFError as e:
                #print(type(e))
                if type(e) == type(EOFError):
                    print("EOF")
                    return None
                truncated=True
            except Exception as e:
                print(type(e))
                time.sleep(5)
                return None
        return data

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