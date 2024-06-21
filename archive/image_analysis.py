import sys
import numpy as np
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QLineEdit
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

class ImageAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = None
        self.temp_image = None  # For dynamic drawing
        self.scale_factor = None
        self.start_point = None
        self.end_point = None
        self.is_drawing = False  # Track whether we're currently drawing

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Dimension Analyzer')
        self.setGeometry(100, 100, 800, 600)

        # Layout and widgets
        layout = QVBoxLayout()

        # Button to load image
        loadButton = QPushButton('Load Image', self)
        loadButton.clicked.connect(self.loadImage)
        layout.addWidget(loadButton)

        # Known length input
        self.lengthInput = QLineEdit(self)
        self.lengthInput.setPlaceholderText('Enter known length in cm')
        layout.addWidget(self.lengthInput)

        # Button to set the known length
        setLengthButton = QPushButton('Set Known Length', self)
        setLengthButton.clicked.connect(self.setKnownLength)
        layout.addWidget(setLengthButton)

        # Label to display images
        self.imageLabel = QLabel(self)
        self.imageLabel.setFixedSize(1280, 1280)
        layout.addWidget(self.imageLabel)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.show()
        self.raise_()
        self.activateWindow()

    def loadImage(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home', "Image files (*.jpg *.png)")
        if fname:
            self.image = cv2.imread(fname, cv2.IMREAD_COLOR)
            self.temp_image = self.image.copy()  # Create a copy for drawing
            self.displayImage()

    def displayImage(self, image=None):
        if image is None:
            image = self.image
        if image is not None:
            qformat = QImage.Format_RGB888 if image.shape[2] == 3 else QImage.Format_Indexed8
            outImage = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], qformat)
            outImage = outImage.rgbSwapped()
            self.imageLabel.setPixmap(QPixmap.fromImage(outImage))

    def setKnownLength(self):
        try:
            known_length = float(self.lengthInput.text())
            if known_length > 0 and self.start_point and self.end_point:
                pixel_length = np.linalg.norm(np.array(self.start_point) - np.array(self.end_point))
                self.scale_factor = pixel_length / known_length
                print(f"Scale factor set: {self.scale_factor} pixels per cm")
        except ValueError:
            print("Invalid input for known length.")

    def mousePressEvent(self, event):
        # Adjust coordinates relative to the image label
        if event.button() == Qt.LeftButton and self.image is not None:
            self.start_point = self.mapToImageCoordinates(event.pos())
            print(self.start_point)
            self.is_drawing = True

    def mouseMoveEvent(self, event):
        if self.is_drawing and self.image is not None:
            end_point = self.mapToImageCoordinates(event.pos())
            self.temp_image = self.image.copy()
            cv2.line(self.temp_image, self.start_point, end_point, (255, 0, 0), 2)
            self.displayImage(self.temp_image)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None and self.is_drawing:
            self.end_point = self.mapToImageCoordinates(event.pos())
            cv2.line(self.image, self.start_point, self.end_point, (255, 0, 0), 2)
            self.displayImage(self.image)
            self.is_drawing = False
            if self.scale_factor:
                pixel_length = np.linalg.norm(np.array(self.end_point) - np.array(self.start_point))
                real_length = pixel_length / self.scale_factor
                print(f"Measured length: {real_length:.2f} cm")

    def mapToImageCoordinates(self, pos):
        # Convert global position to imageLabel coordinates
        image_pos = self.imageLabel.mapFromParent(pos)
        x, y = image_pos.x(), image_pos.y()-380
        return (x, y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageAnalyzer()
    sys.exit(app.exec_())
