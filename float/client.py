#SLIGHTLY DIFFERENT FROM CURRENTLY DEPLOYED CLIENT

import bluetooth
import json
import threading
import time
import ms5837
import socket
import serial
import subprocess
import sys

st = time.time()

COMPANY_NUMBER = "TRITON007"
dive_number = 0

is_profiling = False

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

class FloatSerial:

    def __init__(self, device="/dev/ttyUSB0", baud_rate=115200, timeout=1):
        self.device = device
        self.baud_rate = baud_rate
        self.timeout = timeout

        self.ser = serial.Serial(self.device, self.baud_rate, timeout=self.timeout)
        self.ser.reset_input_buffer()
    
    def read_serial(self):
        return self.ser.readline().decode('utf-8').rstrip()
    
    def write_serial(self, message):
        self.ser.write(str(list(message)[0]).encode('utf-8'))
        time.sleep(0.05)

class PressureSensor:

    def __init__(self, fluid_density=993):
        self.start_time = time.time()

        self.fluid_density = fluid_density
        
        self.sensor = ms5837.MS5837(model=ms5837.MODEL_30BA, bus=1)
        self.sensor.init()
        self.sensor.setFluidDensity(self.fluid_density)

        self.dive_count = 0
        
        self.packets = []

    def read(self):
        self.sensor.read()
        float_time = time.time()-self.start_time()
        self.dive_count = dive_number
        packet = {"company_number":COMPANY_NUMBER,
                  "float_time":float_time,
                  "pressure":self.sensor.pressure(),
                  "temperature":self.sensor.temperature(), 
                  "depth":self.sensor.depth(),
                  "dive":self.dive_count}
        self.packets.append(packet)
        return packet
    
class CommandListenerThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        kill_process_on_port(self.port)

        self.serial = FloatSerial()

    def connect(self):
        
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind(("", self.port))
        self.sock.listen(1)
    
    def shutdown(self):
        print("Attempting Command Socket Shutdown")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Completed Command Socket Shutdown")

    def run(self):
        global is_profiling

        while True:
            self.connect()
            server_sock, server_info = self.sock.accept()
            print(f"Accepted command connection from {server_info}")
            failed = False
            while not failed:

                try:
                    data = server_sock.recv(1024)
                    command = data.decode("utf-8")
                    print(f"Received command: {command}")
                    if str(list(command)[0])=="p":
                        self.serial.write_serial("i")
                        time.sleep(40)
                        self.serial.write_serial("s")
                        time.sleep(10)
                        self.serial.write_serial("o")
                        time.sleep(40)
                except bluetooth.BluetoothError:
                    self.shutdown()
                    time.sleep(3)
                    failed = True
        
class BlankSensor:

    def __init__(self):
        self.packets = []
    
    def read(self):
        self.packets.append({"company_number":COMPANY_NUMBER,
                  "float_time":"FLOAT_TIME",
                  "pressure":"PRESSURE",
                  "temperature":"TEMPERATURE", 
                  "depth":"DEPTH",
                  "dive":"DIVE"})

class DataGathererThread(threading.Thread):

    def __init__(self, fluid_density, gather_interval):
        threading.Thread.__init__(self)

        self.fluid_density = fluid_density
        self.gather_interval = gather_interval

        try:
            self.sensor = PressureSensor(fluid_density=self.fluid_density)
        except IOError:
            print("IO Error when initializing sensor, using blank sensor instead")
            self.sensor = BlankSensor()

        self.packets = []

    def run(self):
        while True:
            self.sensor.read()
            self.packets = self.sensor.packets
            time.sleep(self.gather_interval)


class DataSenderThread(threading.Thread):
    def __init__(self, port, gatherer: DataGathererThread):
        threading.Thread.__init__(self)
        self.port = port
        kill_process_on_port(self.port)

        self.gatherer = gatherer

    def run(self):
        while True:
            self.connect()
            server_sock, server_info = self.sock.accept()
            print(f"Accepted data connection from {server_info}")
            failed = False
            while not failed:
                try:
                    # Simulate gathering data and sending it back
                    data = self.gatherer.packets
                    self.send_data_in_chunks(server_sock, data)
                    #server_sock.send(json.dumps(gathered_data))
                    time.sleep(5)  # Adjust based on your needs
                except bluetooth.BluetoothError:
                    self.shutdown()
                    time.sleep(3)
                    failed = True
    
    @staticmethod
    def send_data_in_chunks(sock, data):
        sock.sendall(data.encode('utf-8')+"_EODT_:!:_EODT_".encode("utf-8"))
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind(("", self.port))
        self.sock.listen(1)
    
    def shutdown(self):
        print("Attempting Data Socket Shutdown")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Completed Data Socket Shutdown")

class Float:

    def __init__(self, command_port, data_port, fluid_density, gather_interval):
        self.command_port = command_port
        self.data_port = data_port
        self.fluid_density = fluid_density
        self.gather_interval = gather_interval

        self.data_gatherer_thread = DataGathererThread(self.fluid_density, self.gather_interval)
        self.data_gatherer_thread.start()
        print("Initialized data gatherer thread")

        self.command_thread = CommandListenerThread(self.command_port)
        self.command_thread.start()
        print("Initialized command thread")

        self.data_thread = DataSenderThread(self.data_port, gatherer=self.data_gatherer_thread)
        self.data_thread.start()
        print("Initialized data senser thread")
    
    def join(self):
        self.data_thread.join()
        self.command_thread.join()
        self.data_gatherer_thread.join()

        
if __name__ == "__main__":
    f = Float(5, 6, 993, 5)