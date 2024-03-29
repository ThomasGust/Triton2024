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

class Pinger(threading.Thread):

    def __init__(self, command_sender, data_receiver):
        self.command_sender = command_sender
        self.data_receiver = data_receiver

    
    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((target_address, self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()

class CommandSender(threading.Thread):

    def __init__(self, port):
        self.port = port

    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((target_address, self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()

class DataReceiver(threading.Thread):

    def __init__(self, port):
        self.port = port

    def shutdown(self):
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()

        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
    
    
    def connect(self):
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((target_address, self.port))
        self.sock.listen(1)

        self.server_sock, self.server_info = self.sock.accept()

    def reboot(self):
        self.shutdown()
        self.connect()

class Commander:
    
    def __init__(self):
        pass

class RobustSocket:
    @timeout
    def recv(self, sock):
        return sock.recv(1024)
    def recvall(self, sock):
        #If there is a cutoff in the middle of the transmission, we will need to kill this thing
        finished = False
        full_data = b''

        end = "_EODT_:!:_EODT_"
        byte_end = end.encode('utf-8')
        while not finished:
            try:
                data = self.recv(sock)
            except TimeoutError:
                finished=True
                return "BROKEN CONNECTION"
            full_data += data
            finished = byte_end in full_data
        
        deserialized = str(full_data, encoding='utf-8')
        j = deserialized.split(end)[0]

        j = json.loads(j)

        return j