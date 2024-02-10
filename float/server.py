import bluetooth
import uuid
import pickle
# Remember to double click b if you want to reset the connection manually.
# Start the server before starting the client otherwise things can get messed up I think.

#Credit to Albert Huang for providing an example bluetooth server in Python. This follows the same general idea, just modularized and with continous input.
#Most of the interesting code over in this robot happens on the client (raspberry pi), and the motor controller (arduino). I will try to upload the code for these soon.
def generate_uuid():
    uuid4 = uuid.uuid4()
    return uuid4


class BluetoothServer:

    def __init__(self, port, uuid):
        self.port = port
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", self.port))
        self.server_sock.listen(1)

        self.port = self.server_sock.getsockname()[1]

        self.uuid = uuid
        bluetooth.advertise_service(self.server_sock, "FloatServer", service_id=self.uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE])

        self.on = True

    def handle_clients(self):
        print("Waiting for connection on RFCOMM channel: ", self.port)

        while self.on:
            self.handle_client()
    
    def handle_client(self):
        client_sock, client_info = self.server_sock.accept()
        print("Accepted connection from", client_info)

        data = client_sock.recv(65536)
        data = pickle.loads(data)
        print(f"RECEIVED DATA PACKET: {data}")
        #o: stutter out
        #i: stutter in
        #s: stop
        #d: out
        #a: in
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
        except Exception as e:
            pass

        print("Disconnected.")

        client_sock.close()

if __name__ == "__main__":
    print(generate_uuid)
    id = "71c94c53-28c7-43a3-b05f-0ffd96fcd2e3"
    port = bluetooth.PORT_ANY

    server = BluetoothServer(port, id)
    server.handle_clients()