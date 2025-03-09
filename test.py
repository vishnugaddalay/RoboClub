import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, QSize

class FaceRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()
        # self.initUI()
        self.capture = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.recording = False
        self.video_writer = None
        

    # def initUI(self):
        self.setWindowTitle('Face Recognition App')
        self.setGeometry(100, 100, 800, 600)
        
        self.video_label = QLabel(self)
        
        self.capture_button = QPushButton('Capture Photo', self)
        self.capture_button.clicked.connect(self.capture_photo)
        
        self.record_button = QPushButton('Start Recording', self)
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.video_label.setScaledContents(True)
        layout = QVBoxLayout()

        layout.addWidget(self.video_label)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.record_button)
        self.setLayout(layout)

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if self.recording and self.video_writer is not None:
                self.video_writer.write(frame)
            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def capture_photo(self):
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite('captured_photo.jpg', frame)
            print('Photo saved as captured_photo.jpg')

    def toggle_recording(self):
        if self.recording:
            self.recording = False
            self.video_writer.release()
            self.video_writer = None
            self.record_button.setText('Start Recording')
            print('Video recording stopped.')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter('recorded_video.avi', fourcc, 20.0, (640, 480))
            self.recording = True
            self.record_button.setText('Stop Recording')
            print('Video recording started.')

    def closeEvent(self, event):
        self.timer.stop()
        self.capture.release()
        if self.video_writer:
            self.video_writer.release()
        event.accept()
    def resizeEvent(self, a0):
        video_width=int(self.width()*0.8)
        video_h=int(video_width*9/16)
        self.video_label.setFixedSize(QSize(video_width,video_h))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec())
