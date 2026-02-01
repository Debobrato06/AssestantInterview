import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette
from speech_processor import SpeechProcessor
from chat_gpt import ChatGPTAssistant

class InterviewAssistantUI(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = SpeechProcessor()
        self.ai = ChatGPTAssistant()
        self.init_ui()
        
        # Timer to poll for new speech results
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_speech)
        self.timer.start(100)

    def init_ui(self):
        # Window Setup
        self.setWindowTitle("AI Interview Assistant")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(450, 600)

        # Main Layout
        self.layout = QVBoxLayout()
        self.container = QFrame()
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: rgba(30, 30, 35, 230);
                border-radius: 20px;
                border: 2px solid #3d3d45;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4a4ae2;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5af2;
            }
            QTextEdit {
                background-color: rgba(50, 50, 60, 150);
                color: #e0e0e0;
                border-radius: 10px;
                border: 1px solid #4a4ae2;
                padding: 10px;
                font-size: 14px;
            }
        """)
        
        container_layout = QVBoxLayout(self.container)

        # Header (Draggable)
        header_layout = QHBoxLayout()
        self.title_label = QLabel("AI INTERVIEW ASSISTANT")
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("background-color: #ff4d4d; border-radius: 15px;")
        self.close_btn.clicked.connect(self.close)
        header_layout.addWidget(self.close_btn)
        
        container_layout.addLayout(header_layout)

        # Status
        self.status_label = QLabel("Status: Idle")
        container_layout.addWidget(self.status_label)

        # Detected Question
        container_layout.addWidget(QLabel("Last Detected Question:"))
        self.question_box = QTextEdit()
        self.question_box.setReadOnly(True)
        self.question_box.setMaximumHeight(100)
        container_layout.addWidget(self.question_box)

        # AI Answer
        container_layout.addWidget(QLabel("AI Suggested Answer:"))
        self.answer_box = QTextEdit()
        self.answer_box.setReadOnly(True)
        container_layout.addWidget(self.answer_box)

        # Controls
        self.listen_btn = QPushButton("START LISTENING")
        self.listen_btn.clicked.connect(self.toggle_listening)
        container_layout.addWidget(self.listen_btn)

        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        # Dragging logic
        self.oldPos = self.pos()
        
        # Print devices
        self.list_audio_devices()

    def list_audio_devices(self):
        print("Available Audio Devices:")
        import sounddevice as sd
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            print(f"{i}: {d['name']} ({d['hostapi_name']})")

    def toggle_listening(self):
        if not self.processor.is_listening:
            self.processor.start_listening()
            self.listen_btn.setText("STOP LISTENING")
            self.listen_btn.setStyleSheet("background-color: #e24a4a;")
            self.status_label.setText("Status: Listening...")
        else:
            self.processor.stop_listening()
            self.listen_btn.setText("START LISTENING")
            self.listen_btn.setStyleSheet("background-color: #4a4ae2;")
            self.status_label.setText("Status: Idle")

    def process_speech(self):
        text = self.processor.get_latest_text()
        if text:
            self.question_box.setText(text)
            self.status_label.setText("Status: Generating Answer...")
            answer = self.ai.get_answer(text)
            self.answer_box.setText(answer)
            self.status_label.setText("Status: Listening...")

    # Drag window methods
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterviewAssistantUI()
    window.show()
    sys.exit(app.exec())
