#!/usr/bin/env python3
"""
Enhanced VyomFix Desktop Launcher
Run this script to launch the enhanced version with chat panel and better graphs
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_enhanced import VyomFixDesktop
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPalette, QColor
    
    print("🚀 Starting VyomFix Desktop - Enhanced Version")
    print("Features:")
    print("  • Enhanced graph visualization with clear anomaly detection")
    print("  • Gemini AI-powered root cause analysis chat")
    print("  • Sleek dark theme with orange accents")
    print("  • Modern UI with improved typography")
    print("  • Secure API key management")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 10))
    palette.setColor(QPalette.WindowText, QColor(230, 230, 230))
    palette.setColor(QPalette.Base, QColor(10, 10, 10))
    palette.setColor(QPalette.AlternateBase, QColor(26, 26, 26))
    palette.setColor(QPalette.ToolTipBase, QColor(10, 10, 10))
    palette.setColor(QPalette.ToolTipText, QColor(230, 230, 230))
    palette.setColor(QPalette.Text, QColor(230, 230, 230))
    palette.setColor(QPalette.Button, QColor(26, 26, 26))
    palette.setColor(QPalette.ButtonText, QColor(230, 230, 230))
    palette.setColor(QPalette.BrightText, QColor(255, 140, 66))
    palette.setColor(QPalette.Link, QColor(255, 140, 66))
    palette.setColor(QPalette.Highlight, QColor(255, 140, 66))
    palette.setColor(QPalette.HighlightedText, QColor(10, 10, 10))
    app.setPalette(palette)
    
    window = VyomFixDesktop()
    window.show()
    
    print("✅ Application started successfully!")
    print("💡 Tip: Use the 'Analysis Chat' tab to ask about flight anomalies")
    print("🔧 Configure your Gemini API key in the Admin panel for full AI functionality")
    
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1) 