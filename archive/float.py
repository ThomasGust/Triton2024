#Robustness is the name of the game here, this has to work no matter what disconnects occur 

import bluetooth
import pickle as pkl
import os
import sys
import json
import subprocess
import threading
import ms5837
import serial
import time
import socket
import errno
import os
import signal
import functools

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


st = time.time()

COMPANY_NUMBER = "TRITON007"
dive_number = 0

ping = False

class ArduinoSerial:

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

class CommandListener(threading.Thread):
    
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

        self.ser = ArduinoSerial()
        self.connect()
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind(("", self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()
    
    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    def reboot(self):
        self.shutdown()
        self.connect()
    
    @timeout
    def recv(self):
        return self.server_sock.recv(1024)

    def run(self):
        global ping
        while True:
            try:
                self.connect()
                while True:
                    if ping:
                        try:
                            data = self.recv()
                        except TimeoutError:
                            ping = False

                        data = str(data, encoding='utf-8')
                        char = str(list(data)[0]).lower()

                        if char == "p":
                            self.ser.write_serial("i")
                            time.sleep(40)
                            self.ser.write_serial("s")
                            time.sleep(40)
                            self.ser.write_serial("o")
                        
                        else:
                            self.ser.write_serial(char)
                        
                    time.sleep(1)
            except Exception as e:
                print(e)
                self.reboot()


class Sensor:
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

class DataGatherer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sensor = Sensor()
    
        self.data = []
    
    def run(self):
        while True:
            self.data.append(self.sensor.read())
            time.sleep(2)


class DataSender(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

        #self.connect()

        self.dg = DataGatherer()
        self.dg.run()
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind(("", self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()
    
    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    def reboot(self):
        self.shutdown()
        self.connect()

    def run(self):
        while True:
            try:
                self.connect()
                while True:
                    if ping:
                        self.sendall(self.dg.data)
                    time.sleep(2)
            except Exception as e:
                print(e)
                self.reboot()

    @timeout
    def sendall(self, data):
        self.server_sock.sendall(str(json.dumps(data)+"_EODT_:!:_EODT_", ).encode('utf-8'))

            
class Pinger(threading.Thread):
    
    def __init__(self, port, command_listener: CommandListener, data_sender: DataSender):
        threading.Thread.__init__(self)
        self.port = port

        self.command_listener = command_listener
        self.data_sender = data_sender
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.bind(("", self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()
    
    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    def reboot(self):
        self.shutdown()
        self.connect()

    @timeout
    def send_ping(self):
        self.server_sock.send("p".encode('utf-8'))
    
    @timeout
    def recv(self):
        return self.server_sock.recv(1024)

    def connectall(self):
        self.data_sender.connect()
        print("Data sender connection was established")
        self.command_listener.connect()
        print("Command Listener connection was established")
    def run(self):
        global ping

        self.ping_start_time = time.time()
        
        while True:
            connected = False
            while not connected:
                try:
                    self.connect()
                    connected=True
                    print("Ping connection was re-established")
                    self.connectall()
                    ping = True
                except Exception as e:
                    connected=False
                    print(f"{type(e)} when attempting reconnection")
                time.sleep(1)

            while ping:
                self.send_ping()
                try:
                    self.recv()
                except TimeoutError:
                    if ping:
                        print("Lost connection on ping thread")
                        ping = False
                        self.data_sender.shutdown()
                        print("Data sender has been shut down")
                        self.command_listener.shutdown()
                        print("Command listener has been shutdown")
                        self.shutdown()
                        print("pinger has been shutdown")
class Float:
    
    def __init__(self):
        self.command_listener = CommandListener(6)
        self.data_sender = DataSender(7)

        self.pinger = Pinger(5, self.command_listener, self.data_sender)


    def start(self):
        self.pinger.start()
        self.pinger.command_listener.start()
        self.pinger.data_sender.start()
    
    def connect(self):
        self.pinger.connect()
        self.pinger.command_listener.connect()
        self.pinger.data_sender.connect()
    
    def shutdown(self):
        self.pinger.shutdown()
        self.pinger.command_listener.shutdown()
        self.pinger.data_sender.shutdown()
    
    def reboot(self):
        self.shutdown()
        self.connect()
    
    def join(self):
        self.pinger.join()
        self.pinger.command_listener.join()
        self.pinger.data_sender.join()

if __name__ == "__main__":
    floaty = Float()
    floaty.start()