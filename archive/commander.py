import bluetooth
import pickle as pkl
import os
import sys
import json
import subprocess
import threading
import socket
import errno
import functools
import signal
import time

ping = False

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
        

class CommandSender(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((target_address, self.port))
        #self.sock.listen(1)

        #self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()
    
    @timeout
    def send(self, data):
        self.server_sock.send(str(data).encode('utf-8'))
    
    def run(self):
        global ping
        while True:
            if ping:
                cmd_input = input("Please enter a command below: ")

                if ping:
                    try:
                        self.send(cmd_input)
                    except TimeoutError:
                        ping = False
            time.sleep(1)

class DataReceiver(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((target_address, self.port))
        #self.sock.listen(1)

        #self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()
    
    @timeout()
    def recv(self):
        return self.server_sock.recv(1024)
    
    def recvall(self):
        #If there is a cutoff in the middle of the transmission, we will need to kill this thing
        finished = False
        full_data = b''

        end = "_EODT_:!:_EODT_"
        byte_end = end.encode('utf-8')
        while not finished:
            try:
                data = self.recv()
            except TimeoutError:
                finished=True
                return "BROKEN CONNECTION"
            print(data)
            full_data += data
            finished = byte_end in full_data
        
        deserialized = str(full_data, encoding='utf-8')
        j = deserialized.split(end)[0]

        j = json.loads(j)

        return j

    def run(self):
        global ping
        while True:
            if ping:
                j = self.recvall()
                if j == "BROKEN CONNECTION":
                    ping = False
                else:
                    json.dump(j, "log.json")
            time.sleep(2)

class Pinger(threading.Thread):

    def __init__(self, port, command_sender:CommandSender, data_receiver:DataReceiver):
        threading.Thread.__init__(self)
        
        self.command_sender = command_sender
        self.data_receiver = data_receiver

        self.port = port
    
    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    def connect(self): 
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((target_address, self.port))
        #self.sock.listen(1)

        #self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()
    
    @timeout
    def recv(self):
        self.server_sock.recv(1024)

    @timeout
    def send_ping(self):
        self.server_sock.send("p".encode('utf-8'))

    def connectall(self):
        self.data_receiver.connect()
        print("Data receiver connection was established")
        self.command_sender.connect()
        print("Command listener connection was established")

    def run(self):
        global ping
        while True:
            connected = False
            while not connected:
                try:
                    self.connect()
                    print("Ping connection was re-established")
                    self.connectall()
                    ping = True
                except Exception as e:
                    connected=False
                    print(f"{type(e)} when attempting reconnection")
                    print(e)
                time.sleep(1)
            while ping:
                self.send_ping()
                try:
                    self.recv()
                except TimeoutError:
                    if ping:
                        print("Lost connection on ping thread")
                        ping = False
                        self.data_receiver.shutdown()
                        print("Data receiver has been shut down")
                        self.command_sender.shutdown()
                        print("Command sender has been shutdown")
                        self.shutdown()
                        print("pinger has been shutdown")


class Commander:
    
    def __init__(self):
        self.command_sender = CommandSender(6)
        self.data_receiver = DataReceiver(7)

        self.pinger = Pinger(5, self.command_sender, self.data_receiver)


    def start(self):
        self.pinger.start()
        self.pinger.command_sender.start()
        self.pinger.data_receiver.start()
    
    def connect(self):
        self.pinger.connect()
        self.pinger.command_sender.connect()
        self.pinger.data_receiver.connect()
    
    def shutdown(self):
        self.pinger.shutdown()
        self.pinger.command_sender.shutdown()
        self.pinger.data_receiver.shutdown()
    
    def reboot(self):
        self.shutdown()
        self.connect()
    
    def join(self):
        self.pinger.join()
        self.pinger.command_sender.join()
        self.pinger.data_receiver.join()

if __name__ == "__main__":
    print(target_address)
    commander = Commander()
    commander.start()