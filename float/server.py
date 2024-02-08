import bluetooth
import uuid
# Remember to double click b if you want to reset the connection manually.
# Start the server before starting the client otherwise things can get messed up I think.
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