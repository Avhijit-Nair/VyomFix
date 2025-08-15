import sys
import os
import json
import threading
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidget, QMessageBox, QInputDialog, QLineEdit, QDialog, QProgressBar, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QTabWidget, QStackedWidget, QTableWidget, QTableWidgetItem, QSplitter, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QMovie, QFont, QColor, QPalette
from folder_watcher import start_watching
from core.pipeline import process_simulation_pdf
import webbrowser
import qtawesome as qta
from core.pipeline import cleanup_generated_code_files
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd

# Import our new components
from root_cause_analyzer import RootCauseAnalyzer
from chat_panel import ChatPanel
from enhanced_graphs import EnhancedGraphVisualizer

CONFIG_FILE = 'config.json'
DATA_DIR = 'data'
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Processing...')
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setStyleSheet('''
            QDialog {
                background: #23293a;
                border-radius: 16px;
                padding: 32px 32px 24px 32px;
            }
            QLabel {
                color: #78dbe2;
                font-size: 17px;
                font-weight: 600;
                margin-bottom: 18px;
            }
            QProgressBar {
                background: #181c24;
                border: 1px solid #2dd4d8;
                border-radius: 8px;
                height: 18px;
                margin-bottom: 12px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #78dbe2);
                border-radius: 8px;
            }
        ''')
        self.layout = QVBoxLayout()
        self.spinner = QLabel()
        self.spinner.setAlignment(Qt.AlignCenter)
        
        # Animated spinner using a bundled GIF
        spinner_path = os.path.join(os.path.dirname(__file__), 'spinner.gif')
        if os.path.exists(spinner_path):
            self.movie = QMovie(spinner_path)
            self.spinner.setMovie(self.movie)
            self.movie.start()
        else:
            self.spinner.setPixmap(QIcon().pixmap(32, 32))
        
        self.status_label = QLabel('Initializing...')
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(4)
        self.progress.setValue(0)
        self.layout.addWidget(self.spinner)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)
        self.resize(350, 160)

    def update_status(self, text, step=None):
        self.status_label.setText(text)
        if step is not None:
            self.progress.setValue(step)

class AdminPanel(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.setWindowTitle('Admin Panel')
        self.setModal(True)
        self.config = config
        self.parent = parent
        self.setStyleSheet('''
            QDialog {
                background: #0a0a0a;
                border-radius: 16px;
                padding: 32px 32px 24px 32px;
                border: 2px solid #333333;
            }
            QLabel {
                color: #e6e6e6;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            QLineEdit {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #ff8c42;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b35, stop:1 #ff8c42);
            }
        ''')
        self.layout = QVBoxLayout()
        
        # Title
        title = QLabel('🔧 API Configuration')
        title.setStyleSheet("""
            QLabel {
                color: #ff8c42;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        self.layout.addWidget(title)
        
        # API Key input
        api_label = QLabel('Gemini API Key:')
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('Enter your Gemini API key')
        self.api_key_input.setText(self.config.get('gemini_api_key', ''))
        self.api_key_input.setEchoMode(QLineEdit.Password)  # Hide the characters
        
        self.layout.addWidget(api_label)
        self.layout.addWidget(self.api_key_input)
        
        # Save button
        self.save_button = QPushButton('💾 Save Configuration')
        self.save_button.clicked.connect(self.save_api_key)
        self.layout.addWidget(self.save_button)
        
        self.setLayout(self.layout)

    def save_api_key(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            self.config['gemini_api_key'] = api_key
            self.parent.save_config()
            # Update the analyzer with new API key
            self.parent.analyzer.set_api_key(api_key)
            print(f"API key updated: {'Yes' if api_key else 'No'}")
            QMessageBox.information(self, 'Success', 'API key saved successfully!')
        else:
            QMessageBox.warning(self, 'Warning', 'Please enter a valid API key.')
        self.accept()

class VyomFixDesktop(QMainWindow):
    status_update = pyqtSignal(str)
    report_refresh = pyqtSignal()
    error_popup = pyqtSignal(str)
    processing_update = pyqtSignal(str, int)
    processing_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.ensure_data_dirs()
        
        # Initialize watcher thread variables
        self.watcher_thread = None
        self.watching = False
        
        # Initialize processing dialog with loading animation
        self.processing_dialog = ProcessingDialog(self)
        
        # Initialize analyzer with API key if available
        gemini_api_key = self.config.get('gemini_api_key', '')
        self.analyzer = RootCauseAnalyzer(api_key=gemini_api_key)
        print(f"Analyzer initialized with API key: {'Yes' if gemini_api_key else 'No'}")
        
        self.graph_visualizer = EnhancedGraphVisualizer()
        self.initUI()
        self.refresh_reports_list()
        
        # Connect signals to slots
        self.status_update.connect(self.set_status)
        self.report_refresh.connect(self.refresh_reports_list)
        self.error_popup.connect(self.show_error_popup)
        self.processing_update.connect(self.show_processing_update)
        self.processing_done.connect(self.hide_processing_dialog)
        
        # Start folder watcher if simulation folder is configured
        if self.config.get('simulation_folder'):
            self.start_folder_watcher(self.config['simulation_folder'])

    def initUI(self):
        # Gradient accent bar
        accent_bar = QFrame()
        accent_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                min-height: 6px;
                max-height: 6px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(accent_bar)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('VyomFix Desktop - Enhanced')
        title.setStyleSheet("""
            QLabel {
                color: #ff8c42;
                font-size: 28px;
                font-weight: bold;
                padding: 20px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Admin button
        admin_button = QPushButton('⚙️ Admin')
        admin_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 16px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b35, stop:1 #ff8c42);
                transform: scale(1.05);
            }
        """)
        admin_button.clicked.connect(self.show_admin_panel)
        header_layout.addWidget(admin_button)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for main content and chat
        splitter = QSplitter(Qt.Horizontal)
        
        # Main content area
        main_content = QWidget()
        main_layout_content = QVBoxLayout()
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.home_button = QPushButton('🏠 Home')
        self.results_button = QPushButton('📊 Results')
        self.compliance_button = QPushButton('📋 Compliance')
        self.chat_button = QPushButton('💬 Analysis Chat')
        
        for button in [self.home_button, self.results_button, self.compliance_button, self.chat_button]:
            button.setStyleSheet("""
                QPushButton {
                    background: #1a1a1a;
                    color: #e6e6e6;
                    border: 2px solid #333333;
                    border-radius: 10px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 16px;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                    color: #ffffff;
                    border: 2px solid #ff8c42;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6b35, stop:1 #ff8c42);
                }
            """)
            button.clicked.connect(lambda checked, b=button: self.navigate_to(b))
        
        nav_layout.addWidget(self.home_button)
        nav_layout.addWidget(self.results_button)
        nav_layout.addWidget(self.compliance_button)
        nav_layout.addWidget(self.chat_button)
        nav_layout.addStretch()
        
        main_layout_content.addLayout(nav_layout)
        
        # Stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Home view
        home_widget = QWidget()
        home_layout = QVBoxLayout()
        
        # Folder selection
        folder_group = QGroupBox("Folder Configuration")
        folder_group.setStyleSheet("""
            QGroupBox {
                color: #e6e6e6;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        folder_layout = QVBoxLayout()
        
        self.baseline_label = QLabel(f"Baseline: {self.config.get('baseline_folder', 'Not set')}")
        self.manual_label = QLabel(f"Manual: {self.config.get('manual_folder', 'Not set')}")
        self.simulation_label = QLabel(f"Simulation: {self.config.get('simulation_folder', 'Not set')}")
        
        for label in [self.baseline_label, self.manual_label, self.simulation_label]:
            label.setStyleSheet("color: #e6e6e6; font-size: 14px; padding: 5px;")
        
        folder_layout.addWidget(self.baseline_label)
        folder_layout.addWidget(self.manual_label)
        folder_layout.addWidget(self.simulation_label)
        
        folder_buttons_layout = QHBoxLayout()
        baseline_btn = QPushButton('Select Baseline')
        manual_btn = QPushButton('Select Manual')
        simulation_btn = QPushButton('Select Simulation')
        
        for btn in [baseline_btn, manual_btn, simulation_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #2dd4d8);
                    color: #e6e6e6;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #78dbe2);
                }
            """)
        
        baseline_btn.clicked.connect(self.select_baseline_folder)
        manual_btn.clicked.connect(self.select_manual_folder)
        simulation_btn.clicked.connect(self.select_simulation_folder)
        
        folder_buttons_layout.addWidget(baseline_btn)
        folder_buttons_layout.addWidget(manual_btn)
        folder_buttons_layout.addWidget(simulation_btn)
        
        folder_layout.addLayout(folder_buttons_layout)
        folder_group.setLayout(folder_layout)
        home_layout.addWidget(folder_group)
        
        # Status
        self.status_label = QLabel('Listening for new simulation data...')
        self.status_label.setStyleSheet("color: #78dbe2; font-size: 16px; padding: 20px;")
        home_layout.addWidget(self.status_label)
        
        home_widget.setLayout(home_layout)
        self.stacked_widget.addWidget(home_widget)
        
        # Results view with enhanced graphs
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        
        # Reports list
        reports_group = QGroupBox("Reports")
        reports_group.setStyleSheet("""
            QGroupBox {
                color: #e6e6e6;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        reports_layout = QVBoxLayout()
        
        self.reports_list = QListWidget()
        self.reports_list.setStyleSheet("""
            QListWidget {
                background: #0f172a;
                color: #e6e6e6;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #334155;
            }
            QListWidget::item:selected {
                background: #2dd4d8;
                color: #0f172a;
            }
        """)
        self.reports_list.itemClicked.connect(self.open_report)
        reports_layout.addWidget(self.reports_list)
        
        # Google Doc button
        self.google_doc_button = QPushButton('📄 Open Google Doc')
        self.google_doc_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #2dd4d8);
                color: #e6e6e6;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #78dbe2);
            }
        """)
        self.google_doc_button.clicked.connect(self.open_google_doc)
        self.google_doc_button.setVisible(False)
        reports_layout.addWidget(self.google_doc_button)
        
        reports_group.setLayout(reports_layout)
        results_layout.addWidget(reports_group)
        
        # Enhanced anomaly visualization
        anomaly_group = QGroupBox("Enhanced Anomaly Detection")
        anomaly_group.setStyleSheet("""
            QGroupBox {
                color: #e6e6e6;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        anomaly_layout = QVBoxLayout()
        
        # Create matplotlib figure for enhanced graphs (1x3 layout like original)
        self.anomaly_fig, self.anomaly_axes = plt.subplots(1, 3, figsize=(18, 6))
        self.anomaly_fig.patch.set_facecolor('#0f172a')
        self.anomaly_canvas = FigureCanvas(self.anomaly_fig)
        self.anomaly_canvas.setStyleSheet("background: #0f172a; border: 1px solid #334155; border-radius: 6px;")
        anomaly_layout.addWidget(self.anomaly_canvas)
        
        anomaly_group.setLayout(anomaly_layout)
        results_layout.addWidget(anomaly_group)
        
        results_widget.setLayout(results_layout)
        self.stacked_widget.addWidget(results_widget)
        
        # Compliance view
        compliance_widget = QWidget()
        compliance_layout = QVBoxLayout()
        
        self.compliance_table = QTableWidget()
        self.compliance_table.setStyleSheet("""
            QTableWidget {
                background: #0f172a;
                color: #e6e6e6;
                border: 1px solid #334155;
                border-radius: 6px;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background: #1e293b;
                color: #e6e6e6;
                padding: 8px;
                border: 1px solid #334155;
            }
        """)
        compliance_layout.addWidget(self.compliance_table)
        
        compliance_widget.setLayout(compliance_layout)
        self.stacked_widget.addWidget(compliance_widget)
        
        # Chat view
        self.chat_panel = ChatPanel(self.analyzer)
        self.stacked_widget.addWidget(self.chat_panel)
        
        main_layout_content.addWidget(self.stacked_widget)
        main_content.setLayout(main_layout_content)
        
        # Add main content to splitter
        splitter.addWidget(main_content)
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Set up central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Window setup
        self.setWindowTitle('VyomFix Desktop - Enhanced')
        self.setGeometry(100, 100, 1600, 1000)
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0a0a;
            }
        """)
        
        # Show home by default
        self.show_home()

    def navigate_to(self, button):
        if button == self.home_button:
            self.show_home()
        elif button == self.results_button:
            self.show_results()
        elif button == self.compliance_button:
            self.show_compliance()
        elif button == self.chat_button:
            self.show_chat()
    
    def show_home(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_button_states(self.home_button)
    
    def show_results(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_button_states(self.results_button)
        self.update_enhanced_anomaly_tab()
    
    def show_compliance(self):
        self.stacked_widget.setCurrentIndex(2)
        self.update_button_states(self.compliance_button)
        self.update_compliance_table()
    
    def show_chat(self):
        self.stacked_widget.setCurrentIndex(3)
        self.update_button_states(self.chat_button)
    
    def update_button_states(self, active_button):
        for button in [self.home_button, self.results_button, self.compliance_button, self.chat_button]:
            if button == active_button:
                button.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                        color: #ffffff;
                        border: 2px solid #ff8c42;
                        border-radius: 10px;
                        padding: 12px 24px;
                        font-weight: bold;
                        font-size: 16px;
                        font-family: 'Segoe UI', 'Arial', sans-serif;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background: #1a1a1a;
                        color: #e6e6e6;
                        border: 2px solid #333333;
                        border-radius: 10px;
                        padding: 12px 24px;
                        font-weight: bold;
                        font-size: 16px;
                        font-family: 'Segoe UI', 'Arial', sans-serif;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff8c42, stop:1 #ff6b35);
                        color: #ffffff;
                        border: 2px solid #ff8c42;
                    }
                """)

    def update_enhanced_anomaly_tab(self):
        """Update enhanced anomaly visualization"""
        item = self.reports_list.currentItem()
        
        if not item:
            # Clear all axes and show placeholder
            for ax in self.anomaly_axes.flat:
                ax.clear()
                ax.axis('off')
            
            # Show placeholder in first subplot
            self.anomaly_axes[0].text(0.5, 0.5, 'No report selected.\nSelect a report to view enhanced anomaly analysis.', 
                                     ha='center', va='center', fontsize=14, color='#e6e6e6',
                                     transform=self.anomaly_axes[0].transAxes)
            self.anomaly_axes[0].axis('off')
            self.anomaly_canvas.draw()
            return
        
        report_name = item.text()
        report_folder = os.path.join(REPORTS_DIR, report_name)
        
        print(f"🔍 Updating graphs for report: {report_name}")
        print(f"   Report folder: {report_folder}")
        
        try:
            # Clear all axes first
            for ax in self.anomaly_axes.flat:
                ax.clear()
            
            # Load and plot data directly
            self._plot_report_data(report_folder)
            
            # Force canvas redraw
            self.anomaly_canvas.draw()
            self.anomaly_canvas.flush_events()
            print("✅ Graphs updated successfully")
            
        except Exception as e:
            print(f"❌ Error updating graphs: {e}")
            # Show error message
            for ax in self.anomaly_axes.flat:
                ax.clear()
                ax.axis('off')
            
            self.anomaly_axes[0].text(0.5, 0.5, f'Error loading graphs:\n{str(e)}', 
                                     ha='center', va='center', fontsize=12, color='#e6e6e6',
                                     transform=self.anomaly_axes[0].transAxes)
            self.anomaly_canvas.draw()
    
    def _plot_report_data(self, report_folder):
        """Plot report data directly on the canvas"""
        # Define chart configurations
        charts = [
            {'title': 'Position (m)', 'ylabel': 'Position (m)', 'type': 'position'},
            {'title': 'Euler Angle (deg)', 'ylabel': 'Euler Angle (deg)', 'type': 'euler'},
            {'title': 'Acceleration (m/s²)', 'ylabel': 'Acceleration (m/s²)', 'type': 'acceleration'}
        ]
        
        colors = [
            ['#ff8c42', '#ff6b35', '#e6e6e6'],  # Position: Northing, Easting, Altitude
            ['#e6e6e6', '#ff6b35', '#ff8c42'],  # Euler: Roll, Pitch, Heading
            ['#e6e6e6', '#ff6b35', '#ff8c42', '#78dbe2']  # Acceleration: x, y, z, Tot
        ]
        legends = [
            ['Northing', 'Easting', 'Altitude'],
            [r'$\phi$ (Roll)', r'$\theta$ (Pitch)', r'$\psi$ (Heading)'],
            ['x', 'y', 'z', 'Tot']
        ]
        
        for idx, chart in enumerate(charts):
            ax = self.anomaly_axes[idx]
            ax.clear()
            
            # Setup axis style
            ax.set_facecolor('#0a0a0a')
            ax.grid(True, alpha=0.2, color='#333333')
            ax.tick_params(colors='#e6e6e6')
            for spine in ax.spines.values():
                spine.set_color('#333333')
                spine.set_linewidth(1)
            
            # Load data
            real_csv = f"{report_folder}/df_chart_{idx+1}_real.csv"
            sim_csv = f"{report_folder}/df_chart_{idx+1}_simulated.csv"
            
            if os.path.exists(real_csv) and os.path.exists(sim_csv):
                print(f"   Loading data from: {real_csv} and {sim_csv}")
                
                df_real = pd.read_csv(real_csv)
                df_sim = pd.read_csv(sim_csv)
                
                # Find time column
                time_col = None
                for candidate in ['Time (s)', 'time', 't', 'Time']:
                    if candidate in df_real.columns:
                        time_col = candidate
                        break
                
                if time_col:
                    # Plot each column
                    cols = [col for col in df_real.columns if col != time_col]
                    for j, col in enumerate(cols):
                        color = colors[idx][j % len(colors[idx])]
                        label = legends[idx][j] if j < len(legends[idx]) else col
                        
                        # Plot real and simulated data
                        ax.plot(df_real[time_col], df_real[col], 
                               color=color, linewidth=2, 
                               label=f'Real {label}')
                        ax.plot(df_sim[time_col], df_sim[col], 
                               color=color, linewidth=2, 
                               linestyle='--', alpha=0.7, 
                               label=f'Sim {label}')
                        
                        # Detect and highlight anomalies
                        self._highlight_anomalies(ax, df_real[time_col], df_real[col], df_sim[col])
                    
                    # Style the plot
                    ax.set_title(chart['title'], fontsize=12, 
                               color='#e6e6e6', fontweight='bold')
                    ax.set_ylabel(chart['ylabel'], fontsize=10, color='#e6e6e6')
                    ax.set_xlabel('Time (s)', fontsize=10, color='#e6e6e6')
                    
                    # Add legend
                    ax.legend(fontsize=8, frameon=True, 
                             facecolor='#1e293b', edgecolor='#333333',
                             loc='best')
                else:
                    ax.text(0.5, 0.5, "No time column found", 
                           ha='center', va='center', fontsize=12, color='#e6e6e6',
                           transform=ax.transAxes)
                    ax.axis('off')
            else:
                ax.text(0.5, 0.5, f"Chart {idx+1} data not available", 
                       ha='center', va='center', fontsize=12, color='#e6e6e6',
                       transform=ax.transAxes)
                ax.axis('off')
    
    def _highlight_anomalies(self, ax, time_data, real_data, sim_data):
        """Highlight detected anomalies"""
        min_len = min(len(time_data), len(real_data), len(sim_data))
        if min_len > 0:
            diff = np.abs(real_data[:min_len] - sim_data[:min_len])
            threshold = diff.mean() + 2*diff.std()
            anomalies = diff > threshold
            
            if anomalies.any():
                # Highlight anomaly regions
                ax.fill_between(time_data[:min_len], 
                              real_data[:min_len], 
                              sim_data[:min_len], 
                              where=anomalies, 
                              color='#ff4757', 
                              alpha=0.4, 
                              label='Detected Anomaly')
                
                # Add anomaly markers
                anomaly_times = time_data[:min_len][anomalies]
                anomaly_values = real_data[:min_len][anomalies]
                ax.scatter(anomaly_times, anomaly_values, 
                          color='#ff4757', 
                          s=30, alpha=0.8, zorder=5)

    def update_compliance_table(self):
        import csv
        item = self.reports_list.currentItem()
        if not item:
            self.compliance_table.setRowCount(0)
            self.compliance_table.setColumnCount(0)
            return
        report_folder = os.path.join(REPORTS_DIR, item.text())
        csv_path = os.path.join(report_folder, 'compliance_mapping_report.csv')
        if not os.path.exists(csv_path):
            self.compliance_table.setRowCount(0)
            self.compliance_table.setColumnCount(0)
            return
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if not reader:
                self.compliance_table.setRowCount(0)
                self.compliance_table.setColumnCount(0)
                return
            headers = reader[0]
            self.compliance_table.setColumnCount(len(headers))
            self.compliance_table.setHorizontalHeaderLabels(headers)
            self.compliance_table.setRowCount(len(reader) - 1)
            for row_idx, row in enumerate(reader[1:]):
                for col_idx, cell in enumerate(row):
                    self.compliance_table.setItem(row_idx, col_idx, QTableWidgetItem(cell))
        self.compliance_table.resizeColumnsToContents()

    def select_baseline_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Baseline Folder')
        if folder:
            self.config['baseline_folder'] = folder
            self.baseline_label.setText(f"Baseline: {folder}")
            self.save_config()

    def select_manual_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Manual Folder')
        if folder:
            self.config['manual_folder'] = folder
            self.manual_label.setText(f"Manual: {folder}")
            self.save_config()

    def select_simulation_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Simulation Folder')
        if folder:
            self.config['simulation_folder'] = folder
            self.simulation_label.setText(f"Simulation: {folder}")
            self.save_config()
            self.start_folder_watcher(folder)

    def open_google_doc(self):
        item = self.reports_list.currentItem()
        if not item:
            return
        report_name = item.text()
        report_folder = os.path.join(REPORTS_DIR, report_name)
        url_file = os.path.join(report_folder, 'google_doc_url.txt')
        if os.path.exists(url_file):
            with open(url_file, 'r') as f:
                url = f.read().strip()
            webbrowser.open(url)

    def update_google_doc_button(self):
        item = self.reports_list.currentItem()
        if not item:
            self.google_doc_button.setVisible(False)
            return
        report_name = item.text()
        report_folder = os.path.join(REPORTS_DIR, report_name)
        url_file = os.path.join(report_folder, 'google_doc_url.txt')
        self.google_doc_button.setVisible(os.path.exists(url_file))

    def start_folder_watcher(self, folder):
        if self.watcher_thread and self.watcher_thread.is_alive():
            self.status_update.emit('Already watching a folder.')
            return
        
        def process_simulation_pdf_callback(pdf_path):
            self.status_update.emit(f'Processing: {os.path.basename(pdf_path)}')
            try:
                baseline_folder = self.config.get('baseline_folder')
                compliance_folder = self.config.get('manual_folder')
                output_dir = REPORTS_DIR
                api_key = self.config.get('gemini_api_key')
                
                if not baseline_folder or not compliance_folder:
                    self.status_update.emit('Baseline and compliance manual folders must be set.')
                    return
                
                self.processing_update.emit('Extracting images from PDFs...', 1)
                report_folder, doc_url = process_simulation_pdf(
                    pdf_path, baseline_folder, compliance_folder, output_dir, api_key
                )
                self.processing_update.emit('Calling Gemini AI for image analysis...', 2)
                self.processing_update.emit('Analyzing compliance...', 3)
                self.processing_update.emit('Saving report...', 4)
                self.status_update.emit(f'Report generated: {os.path.basename(report_folder)}')
                self.report_refresh.emit()
            except Exception as e:
                self.status_update.emit(f'Error: {str(e)}')
                self.error_popup.emit(str(e))
            finally:
                self.processing_done.emit()
                self.status_update.emit('Listening for new simulation data...')
        
        self.watcher_thread = threading.Thread(target=start_watching, args=(folder, process_simulation_pdf_callback), daemon=True)
        self.watcher_thread.start()
        self.status_update.emit(f'Watching folder: {folder}')

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def ensure_data_dirs(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def refresh_reports_list(self):
        self.reports_list.clear()
        if os.path.exists(REPORTS_DIR):
            for item in os.listdir(REPORTS_DIR):
                if os.path.isdir(os.path.join(REPORTS_DIR, item)):
                    self.reports_list.addItem(item)

    def open_report(self, item):
        self.update_enhanced_anomaly_tab()
        self.update_compliance_table()
        self.update_google_doc_button()

    def show_admin_panel(self):
        dialog = AdminPanel(self, self.config)
        dialog.exec_()

    def set_status(self, text):
        self.status_label.setText(text)
    
    def show_error_popup(self, message):
        QMessageBox.critical(self, 'Error', message)
    
    def show_processing_update(self, text, step):
        self.processing_dialog.update_status(text, step)
        if not self.processing_dialog.isVisible():
            self.processing_dialog.show()
    
    def hide_processing_dialog(self):
        self.processing_dialog.hide()

if __name__ == '__main__':
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
    try:
        sys.exit(app.exec_())
    finally:
        cleanup_generated_code_files() 