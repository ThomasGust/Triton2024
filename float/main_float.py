import time
START_TIME = time.time()

import bluetooth
import json
import threading

import ms5837
import socket
import serial
import subprocess
import sys
import numpy as np

COMPANY_NUMBER = "TRITON"
dive_number = 0
depth = 0.0
#HOSTADDR = "00:1A:7D:DA:71:13"
HOSTADDR = "B8:27:EB:A2:69:06"

is_profiling = False

_positions = []
_times = []

last_command=None

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

def compute_velocity(positions, time):
	#Takes velocity with respect to time
	velocities = []
	
	for i in range(len(positions))-1:
		velocity = (positions[i+1]-positions[i])/(time[i+1]-time[i])
		velocities.append(velocity)
	
	return velocities
		
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
        self.fluid_density = fluid_density
        
        self.sensor = ms5837.MS5837(model=ms5837.MODEL_30BA, bus=1)
        self.sensor.init()
        self.sensor.setFluidDensity(self.fluid_density)

        self.dive_count = 0
        
        self.packets = []

    def configure(self):
        self.sensor = ms5837.MS5837(model=ms5837.MODEL_30BA, bus=1)
        self.sensor.init()
        self.sensor.setFluidDensity(self.fluid_density)

    def read(self):
        global depth
        global _times
        global _positions
        #global velocity
        
        try:
            self.sensor.read()
        except IOError:
            errored = True
            while errored:
                try:
                    print("IO Error When Reading Sensor, re-initializing")
                    time.sleep(2)
                    self.configure()
                    time.sleep(1)
                    self.sensor.read()
                    errored = False
                except IOError:
                    errored = True

        float_time = time.time()-START_TIME
        self.dive_count = dive_number

        depth = self.sensor.depth()
        packet = {"company_number":COMPANY_NUMBER,
                  "float_time":float_time,
                  "pressure":self.sensor.pressure(),
                  "temperature":self.sensor.temperature(), 
                  "depth":depth,
                  "dive":self.dive_count,
                  "lc":last_command}
        
        _times.append(float_time)
        _positions.append(depth)
        
        if len(packets) > 10:
            packets = packets[-10:]
			
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

        self.sock.bind((HOSTADDR, self.port))
        self.sock.listen(1)
    
    def shutdown(self):
        print("Attempting Command Socket Shutdown")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Completed Command Socket Shutdown")

    def run(self):
        global is_profiling
        global dive_number
        global last_command

        while True:
            self.connect()
            server_sock, server_info = self.sock.accept()
            print(f"Accepted command connection from {server_info}")
            failed = False
            while not failed:

                try:
                    data = server_sock.recv(1024)
                    inp = data.decode("utf-8")

                    inp  = json.loads(inp)
                    command = inp['command']
                    params = inp['params']

                    print(f"Received command: {command}")
                    last_command = command

                    print(command)
                    
                    if command == "c":
                        dive_number += 1

                        self.serial.write_serial("i")
                        time.sleep(params['in_time'])

                        self.serial.write_serial("s")
                        time.sleep(params['sleep_time'])

                        self.serial.write_serial("o")
                        time.sleep(params['out_time'])

                        self.serial.write_serial("s")

                    if command == "y":
                        actions = params["actions"]

                        for action in actions:
                            action = str(action)

                            if action.isdigit():
                                time.sleep(float(action))
                            
                            else:
                                self.serial.write_serial(action)
                        
                        self.serial.write_serial("o")

                    if command == "p":
						#TODO, THIS PROFILE SHOULD BE SMARTER
                        dive_number += 1

                        out_flag = True
                        
                        cntr = 0
                        while out_flag:
                            self.serial.write_serial("i")
							
                            velocity = compute_velocity(_positions, _times)
                            velocity = velocity[-1]
                            depth = _positions[-1]
							
                            if depth >= params['stall_depth_limit'] and velocity >= params['stall_velocity_limit']:
                                out_flag = False
                                self.serial.write_serial("s")
							
                            
                            if cntr >= params['stall_cntr_limit']:
                                out_flag = False
                                self.serial.write_serial("s")
                            cntr += 1
                            time.sleep(0.5)
						
                        pause_flag = False
                        
                        cntr = 0
                        while not pause_flag:
							
                            velocity = compute_velocity(_positions, _times)
                            velocity = velocity[-1]
							
                            depth = _positions[-1]
							
							
                            if depth >= params['bottom_depth_limit'] and velocity <= params['bottom_velocity_limit']:
                                pause_flag = True

                            if cntr >= params['bottom_cntr_limit']:
                                pause_flag = True

                            time.sleep(0.5)
                        
                        time.sleep(params['bottom_time'])

                        self.serial.write_serial("o")
                        time.sleep(params['up_time'])

                        self.serial.write_serial("s")
                    else:
                        self.serial.write_serial(command)
                
                except bluetooth.BluetoothError:
                    self.shutdown()
                    time.sleep(3)
                    failed = True
        
class BlankSensor:

    def __init__(self):
        self.packets = []
    
    def read(self):
        self.packets.append({"company_number":COMPANY_NUMBER,
                  "float_time":time.time()-START_TIME,
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
                    data = self.gatherer.packets
                    data = data[::5] #Send every fifth sensor packet

                    self.send_data_in_chunks(server_sock, data)

                    time.sleep(5)
                except bluetooth.BluetoothError:
                    self.shutdown()
                    time.sleep(3)
                    failed = True
    
    @staticmethod
    def send_data_in_chunks(sock, data):
        sock.sendall(json.dumps(data).encode('utf-8')+"_EODT_:!:_EODT_".encode("utf-8"))
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind((HOSTADDR, self.port))
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
    f = Float(5, 6, 993, 0.5)
