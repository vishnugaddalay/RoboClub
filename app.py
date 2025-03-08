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
        self.record_timer=QTimer(self)
        self.record_timer.timeout.connect(self.record_frame)
        self.recording = False
        self.video_writer = None
        self.setMinimumSize(200, 200)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
    def capturePicture(self):
            ret, frame = self.capture.read()
            cv2.imwrite(f"{int(time.time())}.png", frame)

    def start_recording(self):
        if not self.recording:
            self.recording = True
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(f"{int(time.time())}.avi", fourcc, 15.0, (1920, 1080))
            self.record_timer.start(int(1000/15))

    def record_frame(self):
        if self.recording:
            ret, frame = self.capture.read()
            if ret:
                self.video_writer.write(frame)

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.record_timer.stop()
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None


    def closeEvent(self, event):
        self.capture.release()
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera")
        self.setMinimumSize(800,480)

        self.cam = Camera()
        self.record = QPushButton("Start Recording")
        self.cap_picture = QPushButton("Capture Picture")

        self.record.setCheckable(True)
        self.record.setFixedSize(100,100)
        self.record.clicked.connect(self.record_func)
        self.cap_picture.setFixedSize(100,100)
        self.cap_picture.clicked.connect(self.cam.capturePicture)

        main_layout = QHBoxLayout()
        buttons = QVBoxLayout()

        buttons.addWidget(self.record)
        buttons.addWidget(self.cap_picture)
        main_layout.addWidget(self.cam)
        main_layout.addLayout(buttons)

        self.container = QWidget()
        self.container.setLayout(main_layout)
        self.setCentralWidget(self.container)

    def resizeEvent(self, event):
        cam_w = int(self.width() * 0.9)
        cam_h = int(cam_w*9/16)
        self.cam.resize(cam_w, cam_h)
    def record_func(self):
        if self.record.isChecked():
            self.record.setText("Stop Recording")
            self.cam.start_recording()
        else:
            self.record.setText("Start Recording")
            self.cam.stop_recording()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

