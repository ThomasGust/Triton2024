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




class DataListenerThread(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)

        self.port = port

class CommandSenderThread(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)

        self.port = port