from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton 
from PyQt6.QtGui import *
from PyQt6.QtCore import QTimer, Qt, QSize
import cv2
import sys
import time

class Camera(QLabel):
    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            exit()
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

        self.tim = QTimer(self)
        self.tim.timeout.connect(self.update_frame)
        self.tim.start(30)
        self.update_frame()
        self.setMinimumSize(200,200)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.width(),self.height()))

            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.setPixmap(QPixmap.fromImage(q_image))
    def capturePicture(self):
            ret, frame = self.capture.read()
            cv2.imwrite(f"{int(time.time())}.png", frame)


    def closeEvent(self, event):
        self.capture.release()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera")
        self.cam = Camera()
        main_layout = QVBoxLayout()
        left_layout = QHBoxLayout()
        left_layout.addWidget(self.cam)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.container = QWidget()
        self.container.setLayout(main_layout)
        main_layout.addLayout(left_layout)
        self.setCentralWidget(self.container)
        self.setMinimumSize(QSize(1280,720))
        cam_w = int(self.width() * 0.9)
        cam_h = int(cam_w*9/16)

    def resizeEvent(self, event):
        cam_w = int(self.width() * 0.9)
        cam_h = int(cam_w*9/16)
        self.cam.resize(cam_w, cam_h)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

