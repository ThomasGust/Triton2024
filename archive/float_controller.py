import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QComboBox, QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from new_server import DataThread, CommandThread
import json
import os

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dt = DataThread(5)
        self.ct = CommandThread(6)
        
        self.dt.start()
        self.ct.start()

        self.setWindowTitle("Vertical Profiling Float Controller")
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Command Terminal
        self.command_terminal = QTextEdit()
        self.command_terminal.setPlaceholderText("Enter commands here...")
        self.layout.addWidget(self.command_terminal)

        # Button to send commands
        self.send_command_button = QPushButton("Send Command")
        self.send_command_button.clicked.connect(self.send_command)
        self.layout.addWidget(self.send_command_button)

        # Last Data Packet Display
        self.data_display = QLabel("Last Data Packet: None")
        self.layout.addWidget(self.data_display)

        """
        # Profile Selection Dropdown
        self.profile_dropdown = QComboBox()
        self.profile_dropdown.addItems(["Profile 1", "Profile 2", "Profile 3"])  # Example profiles
        self.profile_dropdown.currentIndexChanged.connect(self.profile_selected)
        self.layout.addWidget(self.profile_dropdown)

        # Graph Display Area (Placeholder for actual graph)
        self.graph_display = QLabel("Graph will be displayed here.")
        self.graph_display.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.graph_display)
        """
        
        self.setup_timer()

    def send_command(self):
        # Placeholder for command sending logic
        command = self.command_terminal.toPlainText()
    
        usr = command.split(",")

        command, params = usr[0], usr[1]
        params = params.replace(" ", "")
        params = json.load(open(params, "r"))

        if command == "":
            command = "s"

        self.sock.send(json.dumps({"command": command, "params":params}))
        print(f"Command sent: {command}")

    def update_data_display(self, data):
        self.data_display.setText(f"Last Data Packet: {data}")

    def profile_selected(self, index):
        # Placeholder for updating graphs based on selected profile
        print(f"Profile {index + 1} selected")

        self.graph_display.setText(f"Graph for Profile {index + 1}")
    
    def close_event(self, event):
        self.dt.shutdown()
        self.ct.shutdown()
        event.accept()
    
    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Timer set for 1000 milliseconds (1 second)
        self.timer.timeout.connect(self.fetch_new_data)
        self.timer.start()

    def fetch_new_data(self):
        # This method should be modified to fetch the actual data
        # For demonstration, we'll simulate data being updated

        log_dir = "float\\logs"
        new_data = os.path.join(log_dir, os.listdir(log_dir)[-1])

        data = json.load(open(new_data, "r"))
        self.update_data_display(data[-1])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
