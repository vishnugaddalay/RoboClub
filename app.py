from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer
import cv2
import sys
import time


class Camera(QLabel):
    def __init__(self):
        super().__init__()

        self.recording = False
        self.cap = False
        self.video_writer = None
        self.capture = cv2.VideoCapture(0)

        if not self.capture.isOpened():
            raise RuntimeError("Failed to open camera.")
        # Set 720p capture
        self.frame_width = 1280
        self.frame_height = 720
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        fourcc = cv2.VideoWriter_fourcc(*"XVID")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setScaledContents(True)

        self.count = 0
        self.face = []
        self.face_classifier = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def draw_boxes(self, ret, frame):
        self.count += 1

        if self.count % 5 != 0:  # Only detect faces every 5 frames
            return frame

        if ret:
            gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small_gray = cv2.resize(gray_image, (0, 0), fx=0.5, fy=0.5)
            self.face = self.face_classifier.detectMultiScale(
                small_gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20)
            )

        return frame

    def update_frame(self):
        ret, frame = self.capture.read()

        if ret:
            frame = self.draw_boxes(ret, frame)

            if self.face is not None:
                for (x, y, w, h) in self.face:
                    x, y, w, h = (
                        2 * x,
                        2 * y,
                        2 * w,
                        2 * h,
                    )  # Did facial recognition on a scaled down version of frame
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if self.recording:
                self.video_writer.write(frame)
            elif self.cap:
                filename = f"{int(time.time())}.png"
                cv2.imwrite(filename, frame)
                print(frame.size)
                self.cap = False

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(
                frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )

            pixmap = QPixmap.fromImage(q_image)
            self.setPixmap(pixmap)

    def capture_picture(self):
        self.cap = True

    def start_recording(self):
        if not self.recording:
            self.recording = True
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self.video_writer = cv2.VideoWriter(
                f"{int(time.time())}.avi",
                fourcc,
                30.0,
                (self.frame_width, self.frame_height),
            )

    def stop_recording(self):
        if self.recording:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

    def close(self):
        if self.recording:
            self.stop_recording()
        self.timer.stop()
        if self.capture.isOpened():
            self.capture.release()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera")
        self.setMinimumSize(800, 480)

        self.cam = Camera()
        self.record_button = QPushButton("Start Recording")
        self.capture_button = QPushButton("Capture Picture")

        self.record_button.setCheckable(True)
        self.record_button.setFixedSize(100, 100)
        self.record_button.clicked.connect(self.toggle_recording)

        self.capture_button.setFixedSize(100, 100)
        self.capture_button.clicked.connect(self.cam.capture_picture)

        main_layout = QHBoxLayout()
        button_layout = QVBoxLayout()

        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.capture_button)

        main_layout.addWidget(self.cam)
        main_layout.addLayout(button_layout)

        self.container = QWidget()
        self.container.setLayout(main_layout)
        self.setCentralWidget(self.container)

    def resizeEvent(self, event):
        max_width = self.width() - 150
        max_height = self.height() - 100

        cam_w = max_width
        cam_h = int(cam_w * 9 / 16)

        if cam_h > max_height:
            cam_h = max_height
            cam_w = int(cam_h * 16 / 9)

        self.cam.setFixedSize(cam_w, cam_h)

        super().resizeEvent(event)

    def toggle_recording(self):
        if self.record_button.isChecked():
            self.record_button.setText("Stop Recording")
            self.cam.start_recording()
        else:
            self.record_button.setText("Start Recording")
            self.cam.stop_recording()

    def closeEvent(self, event):
        self.cam.close()
        event.accept()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
