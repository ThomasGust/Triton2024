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

TARGET_ADDRESS = None
is_profiling = True

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

class DataSenderThread(threading.Thread):

    def __init__(self, port, address):
        threading.Thread.__init__(self)
    
        self.port = port
        self.address = address


class CommandListenerThread(threading.Thread):

    def __init__(self, port, address):
        threading.Thread.__init__(self)
        self.port = port
        self.address =  address
    
    def connect(self):
        print("Attempting Command Listener Thread Connection")
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        self.sock.connect((self.address, self.port))
        #self.sock.listen(1)
        print("Connected Command Listener Thread")

    def shutdown(self):
        print("Attempting Command Socket Shutdown")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        print("Completed Command Socket Shutdown")
    
    def run(self):
        global is_profiling

        while True:
            self.connect()
            
            
class Float:

    def __init__(self, data_sender_port, command_listener_port):
        self.command_thread = CommandListenerThread(command_listener_port, TARGET_ADDRESS)
        self.data_sender = DataSenderThread(data_sender_port, TARGET_ADDRESS)
