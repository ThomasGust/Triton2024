import bluetooth
import uuid
import pickle
import sys
import time
import os
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

    def __init__(self, port, uuid):
        self.port = port
        self.command_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.command_sock.bind(("", self.port))
        self.server_sock.listen(1)

        self.port = self.server_sock.getsockname()[1]

        self.uuid = uuid
        # Instead of running everything over 1 socket, we will be using an architecture where we use multiple sockets to send different data.
        bluetooth.advertise_service(self.server_sock, "FloatServer", service_id=self.uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])

        self.on = True

    def handle_clients(self):
        while self.on:
            print("Waiting for connection on RFCOMM channel: ", self.port)
            self.handle_client()
    
    def handle_client(self):
        client_sock, client_info = self.server_sock.accept()
        print("Accepted connection from", client_info)

        # r TO START SENSOR THREAD
        # q to QUERY THE SENSOR THREAD
        #o: stutter out
        #i: stutter in
        #s: stop
        #d: out
        #a: in
        #x: restart script
        print("o: stutter out")
        print("i: stutter in")
        print("s: stop")
        print("d: out")
        print("a: in")

        #I will add the key for profiling here later.
        try:
            while True:
                cmd = input("Enter Command: ")
                if cmd == "quit":
                    break
                client_sock.send(cmd)
                if cmd == "q":
                    lines = []
                    off = False
                    while not off:
                        data = client_sock.recv(4096)
                        deserialized = pickle.loads(data)
                        print(deserialized)
                        if deserialized == "EOF":
                            off = True
                        else:
                            lines.append(deserialized)
                    
                    log_buffer = lines
                    with open(fname, "wb") as f:
                        pickle.dump(log_buffer, f)
            
                if cmd == "x":
                    client_sock.close()
        except Exception as e:
            print(e)

        print("Disconnected.")

        client_sock.close()

if __name__ == "__main__":
    print(generate_uuid)
    id = "71c94c53-28c7-43a3-b05f-0ffd96fcd2e3"
    port = bluetooth.PORT_ANY

    server = BluetoothServer(port, id)
    server.handle_clients()