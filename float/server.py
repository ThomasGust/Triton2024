import bluetooth
import uuid
import pickle
import sys
import time
import os
import threading
# Remember to double click b if you want to reset the connection manually.
# Start the server before starting the client otherwise things can get messed up I think.

#Credit to Albert Huang for providing an example bluetooth server in Python. This follows the same general idea, just modularized and with continous input.
#Most of the interesting code over in this robot happens on the client (raspberry pi), and the motor controller (arduino). I will try to upload the code for these soon.

#TODO There is a lot more to do here. Firstly, it would probably be a good idea to seperate out different threads for commands and sensor data.
#TODO The server should try to help the client by providing access to the servers RTC. This will help the client to keep track of time better.

def generate_uuid():
    uuid4 = uuid.uuid4()
    return uuid4

fname =  f"float\\logs\\{time.time()}.log"
with open(fname, "x") as f:
    _ = f
log_buffer = []
class BluetoothServer:

    def __init__(self, command_port, command_uuid, sensor_port, sensor_uuid, ping_port, ping_uuid):
        self._command_port = command_port
        self.command_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.command_sock.bind(("", self._command_port))
        self.command_sock.listen(1)
        self.command_port = self.command_sock.getsockname()[1]

        self.command_uuid = command_uuid
        # Instead of running everything over 1 socket, we will be using an architecture where we use multiple sockets to send different data.
        bluetooth.advertise_service(self.command_sock, "FloatServer", service_id=self.command_uuid,
                                    service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])
        
        self._sensor_port = sensor_port
        self.sensor_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sensor_sock.bind(("", self._sensor_port))
        self.sensor_sock.listen(1)
        self.sensor_port = self.sensor_sock.getsockname()[1]

        self.sensor_uuid = sensor_uuid

        bluetooth.advertise_service(self.sensor_sock,"SensorService", service_id=self.sensor_uuid,
                                    service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])
        
        # The purpose of the ping service is to let the rest of the threads understand when the float is in range
        self._ping_port = ping_port
        self.ping_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.ping_sock.bind(("", self._ping_port))
        self.ping_sock.listen(1)
        self.ping_port = self.ping_sock.getsockname()[1]
        
        self.ping_uuid = ping_uuid

        bluetooth.advertise_service(self.ping_sock,"PingService", service_id=self.ping_uuid,
                                    service_classes=[bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])
        
        self.on = True
        self.connectable = True
    
    def command_handler(self):
        while self.on:
            print("Waiting for COMMAND connection on RFCOMM channel: ", self.command_port)
            self.handle_command()

    def sensor_handler(self):
        while self.on:
            print("Waiting for SENSOR connection on RFCOMM channel: ", self.sensor_port)
            self.handle_sensor()
        
    def ping_handler(self):
        while self.on:
            print("Waiting for PING connection on RFCOMM channel: ", self.ping_port)
            self.handle_ping()

    def handle_client(self):
        command_thread = threading.Thread(target=self.command_handler)
        sensor_thread = threading.Thread(target=self.sensor_handler)
        ping_thread = threading.Thread(target=self.ping_handler)
    
        command_thread.start()
        sensor_thread.start()
        ping_thread.start()

        command_thread.join()
        sensor_thread.join()
        ping_thread.join()
    
    def handle_sensor(self):
        # This thread should constantly deserialize any data spat out by the sensor
        # Our client should spit out log data every 5 seconds while it is connected
        sensor_sock, sensor_info = self.sensor_sock.accept()
        print("Accepted SENSOR connection from", sensor_info)

        while self.on:
            #print(self.connectable)
            if self.connectable:
                lines = []
                done = False
                while not done:
                    #print("LOOKING FOR DATA")
                    data = sensor_sock.recv(4096)
                    #print(data)
                    if data == b'':
                        time.sleep(2)
                    
                    else:
                        deserialized = pickle.loads(data)
                        if deserialized == "EOF":
                            done = True
                        else:
                            lines.append(deserialized)
                #print(lines)
                
                # Now we will save the lines to our log file
                with open(fname, "wb") as f:
                    pickle.dump(lines, f)

    def handle_command(self):
        client_sock, client_info = self.command_sock.accept()
        print("Accepted COMMAND connection from", client_info)
        print("o: stutter out")
        print("i: stutter in")
        print("s: stop")
        print("d: out")
        print("a: in")

        #I will add the key for profiling here later.
        while True:
            if self.connectable:
                cmd = input("Enter Command: ")
                if self.connectable:
                    client_sock.send(cmd)
    
    def handle_ping(self):
        ping_sock, ping_info = self.ping_sock.accept()
        #ping_sock.setsockopt(bluetooth.SOL_SOCKET, bluetooth.SO_SNDBUF, 64)

        ping_sock.settimeout(5)

        print("Accepted PING connection from", ping_info)
        while self.on:
            try:
                #print(self.connectable)
                data = ping_sock.recv(64).decode("utf-8")
                #print(data)
                #print(self.connectable)
                if self.connectable == False:
                    print("Server is responding")

                self.connectable = True
                ping_sock.send("pong")
                time.sleep(1)
            except Exception as e:
                #print(e)
                if self.connectable == True:
                    print("Server is not responding")
                self.connectable = True
            time.sleep(0.3)
        
        ping_sock.close()

if __name__ == "__main__":
    command_id = "71c94c53-28c7-43a3-b05f-0ffd96fcd2e3"
    sensor_id = "34267a21-7847-4cda-95fe-8e96dcd6b2b6"
    ping_id = "ca9237cc-7d72-46da-9e8f-33d3e29643aa"

    command_port = bluetooth.PORT_ANY
    sensor_port = bluetooth.PORT_ANY
    ping_port = bluetooth.PORT_ANY

    server = BluetoothServer(command_port, command_id, sensor_port, sensor_id, ping_port, ping_id)
    server.handle_client()
