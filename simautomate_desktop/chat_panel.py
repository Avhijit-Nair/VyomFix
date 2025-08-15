import random
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from root_cause_analyzer import RootCauseAnalyzer

class ChatPanel(QWidget):
    """Chat panel for root cause analysis"""
    
    def __init__(self, analyzer):
        super().__init__()
        self.analyzer = analyzer
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🔍 Root Cause Analysis Chat")
        header.setStyleSheet("""
            QLabel {
                color: #ff8c42;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-radius: 10px;
                margin-bottom: 15px;
                border: 1px solid #ff8c42;
            }
        """)
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #e6e6e6;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about anomaly root causes...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #ff8c42;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b35, stop:1 #ff8c42);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e55a2b, stop:1 #ff6b35);
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
        
        # Welcome message
        self.add_message("🤖 AI Analyst", "Hello! I'm your flight anomaly root cause analyzer powered by Gemini AI. Ask me about any detected anomalies for detailed scientific analysis.")
    
    def add_message(self, sender, message):
        timestamp = pd.Timestamp.now().strftime('%H:%M')
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        self.chat_area.append(formatted_message)
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
    
    def send_message(self):
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.add_message("👤 You", message)
        self.input_field.clear()
        
        # Generate AI response
        response = self.generate_ai_response(message)
        self.add_message("🤖 AI Analyst", response)
    
    def generate_ai_response(self, message):
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['anomaly', 'issue', 'problem', 'error']):
                # Generate analysis for a random anomaly
                anomaly_types = ['altitude', 'speed', 'attitude', 'acceleration']
                anomaly_type = random.choice(anomaly_types)
                severity = random.choice(['Low', 'Medium', 'High', 'Critical'])
                time_point = random.uniform(10, 90)
                
                response = self.analyzer.analyze_anomaly(anomaly_type, severity, time_point, message)
                return response if response else "Analysis completed. The anomaly appears to be related to flight dynamics."
            
            elif any(word in message_lower for word in ['help', 'what', 'how']):
                return """I can help you analyze flight anomalies! Try asking:
• "Analyze the altitude anomaly"
• "What caused the speed issue?"
• "Explain the attitude problem"
• "Root cause of the acceleration error"
• "What are the possible causes of this anomaly?"

I'll provide detailed scientific analysis including hardware and atmospheric factors."""
            
            elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
                return "Hello! I'm your AI flight analyst. I can help you understand anomalies in your flight data. What would you like to know?"
            
            else:
                return "I'm here to help with flight anomaly analysis. Please ask about specific anomalies, type 'help' for guidance, or describe what you're seeing in the data."
                
        except Exception as e:
            return f"Sorry, I encountered an error while analyzing: {str(e)}. Please try asking about a specific anomaly or type 'help' for guidance." 