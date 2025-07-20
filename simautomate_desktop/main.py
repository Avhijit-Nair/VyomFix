import sys
import os
import json
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QVBoxLayout, QWidget, QListWidget, QMessageBox, QInputDialog, QLineEdit, QDialog, QProgressBar, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy, QTabWidget, QStackedWidget, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from folder_watcher import start_watching
from core.pipeline import process_simulation_pdf
import webbrowser
from PyQt5.QtGui import QIcon, QMovie
import qtawesome as qta
from core.pipeline import cleanup_generated_code_files

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
        import os
        spinner_path = os.path.join(os.path.dirname(__file__), 'spinner.gif')
        from PyQt5.QtGui import QPixmap
        if os.path.exists(spinner_path):
            self.movie = QMovie(spinner_path)
            self.spinner.setMovie(self.movie)
            self.movie.start()
        else:
            self.spinner.setPixmap(QPixmap(32, 32))
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
                background: #23293a;
                border-radius: 16px;
                padding: 32px 32px 24px 32px;
            }
            QLabel, QLineEdit {
                color: #e6e6e6;
                font-size: 15px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #2dd4d8);
                color: #e6e6e6;
                border: none;
                border-radius: 12px;
                padding: 10px 18px;
                margin: 8px 0;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #1e293b);
                color: #fff;
            }
        ''')
        layout = QVBoxLayout()
        # API Key
        self.api_label = QLabel('Gemini API Key:')
        self.api_input = QLineEdit()
        self.api_input.setEchoMode(QLineEdit.Password)
        self.api_input.setText(self.config.get('gemini_api_key', ''))
        self.save_btn = QPushButton('Save API Key')
        self.save_btn.clicked.connect(self.save_api_key)
        layout.addWidget(self.api_label)
        layout.addWidget(self.api_input)
        layout.addWidget(self.save_btn)
        # Baseline Folder
        self.baseline_label = QLabel('Baseline Folder:')
        self.baseline_path = QLabel(self.config.get('baseline_folder', 'Not set'))
        self.baseline_btn = QPushButton('Select Baseline Folder')
        self.baseline_btn.clicked.connect(self.select_baseline_folder)
        layout.addWidget(self.baseline_label)
        layout.addWidget(self.baseline_path)
        layout.addWidget(self.baseline_btn)
        # Manual Folder
        self.manual_label = QLabel('Compliance Manual Folder:')
        self.manual_path = QLabel(self.config.get('manual_folder', 'Not set'))
        self.manual_btn = QPushButton('Select Compliance Manual Folder')
        self.manual_btn.clicked.connect(self.select_manual_folder)
        layout.addWidget(self.manual_label)
        layout.addWidget(self.manual_path)
        layout.addWidget(self.manual_btn)
        # Simulation Folder
        self.sim_label = QLabel('Simulation Data Folder to Watch:')
        self.sim_path = QLabel(self.config.get('simulation_folder', 'Not set'))
        self.sim_btn = QPushButton('Select Simulation Data Folder to Watch')
        self.sim_btn.clicked.connect(self.select_simulation_folder)
        layout.addWidget(self.sim_label)
        layout.addWidget(self.sim_path)
        layout.addWidget(self.sim_btn)
        # Reset Button
        self.reset_btn = QPushButton('Reset Folders')
        self.reset_btn.clicked.connect(self.reset_folders)
        layout.addWidget(self.reset_btn)
        self.setLayout(layout)
        self.resize(400, 400)

    def save_api_key(self):
        self.config['gemini_api_key'] = self.api_input.text().strip()
        with open('config.json', 'w') as f:
            json.dump(self.config, f)
        self.accept()

    def select_baseline_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Baseline Folder')
        if folder:
            self.config['baseline_folder'] = folder
            self.baseline_path.setText(folder)
            with open('config.json', 'w') as f:
                json.dump(self.config, f)
            self.parent.status_update.emit(f'Baseline folder set: {folder}')

    def select_manual_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Compliance Manual Folder')
        if folder:
            self.config['manual_folder'] = folder
            self.manual_path.setText(folder)
            with open('config.json', 'w') as f:
                json.dump(self.config, f)
            self.parent.status_update.emit(f'Compliance manual folder set: {folder}')

    def select_simulation_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Simulation Data Folder to Watch')
        if folder:
            self.config['simulation_folder'] = folder
            self.sim_path.setText(folder)
            with open('config.json', 'w') as f:
                json.dump(self.config, f)
            self.parent.status_update.emit(f'Simulation data folder set: {folder}')
            # Prompt for API key in main thread before starting watcher
            api_key = self.config.get('gemini_api_key')
            if not api_key:
                api_key, ok = QInputDialog.getText(self, 'Gemini API Key', 'Enter your Gemini API Key:', echo=QLineEdit.Password)
                if not ok or not api_key:
                    self.parent.status_update.emit('API key required for processing.')
                    return
                self.config['gemini_api_key'] = api_key
                with open('config.json', 'w') as f:
                    json.dump(self.config, f)
            self.parent.start_folder_watcher(folder)

    def reset_folders(self):
        self.config['baseline_folder'] = ''
        self.config['manual_folder'] = ''
        self.config['simulation_folder'] = ''
        with open('config.json', 'w') as f:
            json.dump(self.config, f)
        self.baseline_path.setText('Not set')
        self.manual_path.setText('Not set')
        self.sim_path.setText('Not set')
        self.parent.status_update.emit('All folder paths have been reset.')

class VyomFixDesktop(QMainWindow):
    status_update = pyqtSignal(str)
    report_refresh = pyqtSignal()
    error_popup = pyqtSignal(str)
    processing_update = pyqtSignal(str, int)
    processing_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('VyomFix Compliance Automation (Desktop)')
        self.config = self.load_config()
        self.watcher_thread = None
        self.watching = False
        self.processing_dialog = ProcessingDialog(self)
        self.initUI()
        self.ensure_data_dirs()
        self.refresh_reports_list()
        # Use config folder paths if present
        if self.config.get('baseline_folder'):
            self.status_update.emit(f'Baseline folder set: {self.config["baseline_folder"]}')
        if self.config.get('manual_folder'):
            self.status_update.emit(f'Compliance manual folder set: {self.config["manual_folder"]}')
        if self.config.get('simulation_folder'):
            self.status_update.emit(f'Simulation data folder set: {self.config["simulation_folder"]}')
        # Connect signals to slots
        self.status_update.connect(self.set_status)
        self.report_refresh.connect(self.refresh_reports_list)
        self.error_popup.connect(self.show_error_popup)
        self.processing_update.connect(self.show_processing_update)
        self.processing_done.connect(self.hide_processing_dialog)

    def initUI(self):
        # Gradient accent bar
        accent_bar = QFrame()
        accent_bar.setFixedHeight(8)
        accent_bar.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #78dbe2); border-radius: 4px;')
        # Sidebar layout
        main_layout = QVBoxLayout()
        sidebar = QVBoxLayout()
        sidebar.setSpacing(18)
        sidebar.setContentsMargins(18, 18, 18, 18)
        self.home_btn = QPushButton(qta.icon('fa5s.home', color='#78dbe2'), ' Home')
        self.home_btn.setObjectName('SidebarBtn')
        self.home_btn.clicked.connect(self.show_home)
        self.results_btn = QPushButton(qta.icon('fa5s.chart-bar', color='#78dbe2'), ' Results')
        self.results_btn.setObjectName('SidebarBtn')
        self.results_btn.clicked.connect(self.show_results)
        self.admin_btn = QPushButton(qta.icon('fa5s.cog', color='#78dbe2'), ' Admin Panel')
        self.admin_btn.setObjectName('SidebarBtn')
        self.admin_btn.clicked.connect(self.show_admin_panel)
        self.compliance_btn = QPushButton(qta.icon('fa5s.table', color='#78dbe2'), ' Compliance Mapping')
        self.compliance_btn.setObjectName('SidebarBtn')
        self.compliance_btn.clicked.connect(self.show_compliance)
        sidebar.addWidget(self.home_btn)
        sidebar.addWidget(self.results_btn)
        sidebar.addWidget(self.admin_btn)
        sidebar.addWidget(self.compliance_btn)
        sidebar.addStretch(1)
        # Main content area with stacked pages
        from PyQt5.QtWidgets import QStackedWidget
        self.stacked_pages = QStackedWidget()
        # Home Page
        self.home_page = QWidget()
        home_layout = QVBoxLayout()
        self.status_label = QLabel('Listening for new simulation data...')
        self.status_label.setObjectName('StatusLabel')
        home_layout.addWidget(self.status_label)
        home_layout.addWidget(QLabel('Welcome to VyomFix Compliance Automation!'))
        self.home_page.setLayout(home_layout)
        self.stacked_pages.addWidget(self.home_page)
        # Results Page
        self.results_page = QWidget()
        results_layout = QVBoxLayout()
        # Reports list and anomaly visualization only
        reports_layout = QHBoxLayout()
        # Reports list
        reports_card = QFrame()
        reports_card.setObjectName('Card')
        reports_vbox = QVBoxLayout()
        self.reports_list_label = QLabel('Past Reports:')
        self.reports_list_label.setObjectName('SectionLabel')
        self.reports_list = QListWidget()
        self.reports_list.setObjectName('ReportsList')
        self.reports_list.itemDoubleClicked.connect(self.open_report)
        self.reports_list.currentItemChanged.connect(self.update_results_preview)
        self.reports_list.currentItemChanged.connect(self.update_anomaly_tab)
        self.reports_list.currentItemChanged.connect(self.update_google_doc_button)
        self.reports_list.currentItemChanged.connect(self.update_compliance_table)
        reports_vbox.addWidget(self.reports_list_label)
        reports_vbox.addWidget(self.reports_list)
        reports_card.setLayout(reports_vbox)
        reports_card.setFixedWidth(220)
        reports_layout.addWidget(reports_card)
        # Only Anomaly Visualization (with overlays and deviations)
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        plots_vbox = QVBoxLayout()
        anomaly_label = QLabel('Anomaly Visualization:')
        anomaly_label.setStyleSheet('font-size: 13px; font-weight: bold; margin-bottom: 2px; margin-top: 2px;')
        plots_vbox.addWidget(anomaly_label)
        self.anomaly_fig = Figure(figsize=(12, 4))
        self.anomaly_canvas = FigureCanvas(self.anomaly_fig)
        self.anomaly_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        plots_vbox.addWidget(self.anomaly_canvas, stretch=1)
        reports_layout.addLayout(plots_vbox)
        results_layout.addLayout(reports_layout)
        self.results_page.setLayout(results_layout)
        self.stacked_pages.addWidget(self.results_page)
        # Admin Page
        self.admin_page = QWidget()
        admin_layout = QVBoxLayout()
        admin_layout.addWidget(QLabel('Admin Panel'))
        self.admin_page.setLayout(admin_layout)
        self.stacked_pages.addWidget(self.admin_page)
        # Compliance Mapping Page
        self.compliance_page = QWidget()
        compliance_layout = QVBoxLayout()
        self.compliance_table = QTableWidget()
        self.compliance_table.setColumnCount(0)
        self.compliance_table.setRowCount(0)
        self.compliance_table.setMinimumHeight(400)
        self.compliance_table.setMinimumWidth(800)
        compliance_layout.addWidget(QLabel('Compliance Mapping Table:'))
        compliance_layout.addWidget(self.compliance_table)
        self.compliance_page.setLayout(compliance_layout)
        self.stacked_pages.addWidget(self.compliance_page)
        # Main layout with sidebar
        wrapper = QHBoxLayout()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        sidebar_widget.setFixedWidth(180)
        wrapper.addWidget(sidebar_widget)
        wrapper.addWidget(self.stacked_pages, 1)
        main_container = QVBoxLayout()
        main_container.addWidget(accent_bar)
        main_container.addLayout(wrapper)
        container = QWidget()
        container.setLayout(main_container)
        self.setCentralWidget(container)
        # Set default page
        self.stacked_pages.setCurrentWidget(self.home_page)
        # Enhanced stylesheet for sidebar, cards, gradients, and hover effects
        self.setStyleSheet('''
            QMainWindow { background: #181c24; }
            QWidget { background: #181c24; color: #e6e6e6; font-family: "Segoe UI", "Arial", sans-serif; font-size: 15px; }
            QFrame#Card {
                background: #23293a;
                border-radius: 18px;
                border: 1.5px solid #2dd4d8;
                margin: 18px 0 0 0;
                padding: 18px 24px 18px 24px;
                box-shadow: 0 4px 24px 0 rgba(44, 213, 216, 0.10);
            }
            QPushButton#SidebarBtn {
                background: #23293a;
                color: #78dbe2;
                border: none;
                border-radius: 10px;
                padding: 14px 20px;
                font-size: 17px;
                font-weight: 600;
                margin-bottom: 10px;
                text-align: left;
                transition: all 0.2s;
            }
            QPushButton#SidebarBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #1e293b);
                color: #181c24;
                transform: scale(1.04);
            }
            QFrame, QListWidget#ReportsList {
                background: #23293a;
                border-radius: 16px;
                border: 1px solid #2dd4d8;
                color: #e6e6e6;
                padding: 10px;
                font-size: 15px;
                margin-bottom: 10px;
                box-shadow: 0 4px 24px 0 rgba(44, 213, 216, 0.08);
            }
            QLabel#SectionLabel {
                color: #78dbe2;
                font-size: 18px;
                font-weight: 700;
                margin-top: 18px;
                margin-bottom: 8px;
                letter-spacing: 0.5px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #2dd4d8);
                color: #e6e6e6;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                margin: 6px 0;
                font-weight: 500;
                letter-spacing: 0.5px;
                transition: background 0.3s, transform 0.2s;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2dd4d8, stop:1 #1e293b);
                color: #fff;
                transform: scale(1.03);
                box-shadow: 0 2px 8px 0 rgba(44, 213, 216, 0.12);
            }
        ''')

    def set_status(self, text):
        self.status_label.setText(text)

    def show_error_popup(self, message):
        QMessageBox.warning(self, 'Processing Error', message)

    def show_processing_update(self, text, step):
        self.processing_dialog.update_status(text, step)
        if not self.processing_dialog.isVisible():
            self.processing_dialog.show()

    def hide_processing_dialog(self):
        self.processing_dialog.hide()

    def select_baseline_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Baseline Folder')
        if folder:
            self.config['baseline_folder'] = folder
            self.save_config()
            self.status_update.emit(f'Baseline folder set: {folder}')

    def select_manual_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Compliance Manual Folder')
        if folder:
            self.config['manual_folder'] = folder
            self.save_config()
            self.status_update.emit(f'Compliance manual folder set: {folder}')

    def select_simulation_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Simulation Data Folder to Watch')
        if folder:
            self.config['simulation_folder'] = folder
            self.save_config()
            self.status_update.emit(f'Simulation data folder set: {folder}')
            # Prompt for API key in main thread before starting watcher
            api_key = self.config.get('gemini_api_key')
            if not api_key:
                api_key, ok = QInputDialog.getText(self, 'Gemini API Key', 'Enter your Gemini API Key:', echo=QLineEdit.Password)
                if not ok or not api_key:
                    self.status_update.emit('API key required for processing.')
                    return
                self.config['gemini_api_key'] = api_key
                self.save_config()
            self.start_folder_watcher(folder)

    def open_google_doc(self):
        item = self.reports_list.currentItem()
        if not item:
            return
        report_folder = os.path.join(REPORTS_DIR, item.text())
        doc_url_path = os.path.join(report_folder, 'google_doc_url.txt')
        if os.path.exists(doc_url_path):
            with open(doc_url_path, 'r') as f:
                url = f.read().strip()
            webbrowser.open(url)

    def update_google_doc_button(self):
        if not hasattr(self, 'open_google_doc_btn'):
            return
        item = self.reports_list.currentItem()
        if not item:
            self.open_google_doc_btn.setEnabled(False)
            return
        report_folder = os.path.join(REPORTS_DIR, item.text())
        doc_url_path = os.path.join(report_folder, 'google_doc_url.txt')
        self.open_google_doc_btn.setEnabled(os.path.exists(doc_url_path))

    def update_results_preview(self):
        # No longer needed, as only anomaly visualization is shown
        pass

    def update_anomaly_tab(self):
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        item = self.reports_list.currentItem()
        self.anomaly_fig.clear()
        n_charts = 3
        nrows, ncols = 1, 3
        chart_titles = [
            'Position (m)',
            'Euler Angle (deg)',
            'Acceleration (m/s²)'
        ]
        ylabels = [
            'Position (m)',
            'Euler Angle (deg)',
            'Acceleration (m/s²)'
        ]
        colors = [
            ['b', 'r', 'k'],
            ['k', 'r', 'b'],
            ['k', 'r', 'b', 'c']
        ]
        legends = [
            ['Northing', 'Easting', 'Altitude'],
            [r'$\phi$ (Roll)', r'$\theta$ (Pitch)', r'$\psi$ (Heading)'],
            ['x', 'y', 'z', 'Tot']
        ]
        if not item:
            ax = self.anomaly_fig.add_subplot(1, 1, 1)
            ax.text(0.5, 0.5, 'No report selected.', ha='center', va='center', fontsize=14)
            ax.axis('off')
            self.anomaly_canvas.draw()
            return
        report_name = item.text()
        report_folder = os.path.join(REPORTS_DIR, report_name)
        for i in range(n_charts):
            ax = self.anomaly_fig.add_subplot(nrows, ncols, i+1)
            real_csv = os.path.join(report_folder, f'df_chart_{i+1}_real.csv')
            sim_csv = os.path.join(report_folder, f'df_chart_{i+1}_simulated.csv')
            if not (os.path.exists(real_csv) and os.path.exists(sim_csv)):
                ax.text(0.5, 0.5, f'Chart {i+1} data not found.', ha='center', va='center', fontsize=10)
                ax.axis('off')
                continue
            df_real = pd.read_csv(real_csv)
            df_sim = pd.read_csv(sim_csv)
            # Robust time column detection
            time_col = None
            for candidate in ['Time (s)', 'time', 't', 'Time']:
                if candidate in df_real.columns:
                    time_col = candidate
                    break
            if not time_col:
                ax.text(0.5, 0.5, 'No time column found in data.', ha='center', va='center', fontsize=10)
                ax.axis('off')
                continue
            cols = [col for col in df_real.columns if col != time_col]
            for j, col in enumerate(cols):
                color = colors[i][j % len(colors[i])]
                label = legends[i][j] if j < len(legends[i]) else col
                # Plot full range for real and simulated
                ax.plot(df_real[time_col], df_real[col], color=color, label=f'Real {label}', linewidth=2)
                ax.plot(df_sim[time_col], df_sim[col], color=color, linestyle='--', alpha=0.7, label=f'Sim {label}')
                # Highlight anomalies (only where both real and sim are available)
                min_len = min(len(df_real[time_col]), len(df_sim[time_col]), len(df_real[col]), len(df_sim[col]))
                if min_len > 0:
                    diff = np.abs(df_real[col][:min_len] - df_sim[col][:min_len])
                    threshold = diff.mean() + 2*diff.std()
                    anomalies = diff > threshold
                    if anomalies.any():
                        ax.fill_between(df_real[time_col][:min_len], df_real[col][:min_len], df_sim[col][:min_len], where=anomalies, color='red', alpha=0.3, label='Anomaly' if j == 0 else None)
            ax.set_title(chart_titles[i], fontsize=10)
            ax.set_ylabel(ylabels[i], fontsize=9)
            ax.set_xlabel('Time (s)', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=7, loc='best', frameon=True)
        self.anomaly_fig.tight_layout()
        self.anomaly_canvas.draw()

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

    def open_selected_pdf(self):
        item = self.reports_list.currentItem()
        if not item:
            return
        report_name = item.text()
        report_folder = os.path.join(REPORTS_DIR, report_name)
        pdf_path = None
        if os.path.exists(report_folder):
            for f in os.listdir(report_folder):
                if f.endswith('.pdf'):
                    pdf_path = os.path.join(report_folder, f)
                    break
        if pdf_path:
            try:
                os.startfile(pdf_path)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not open PDF: {e}')

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
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)

    def ensure_data_dirs(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def refresh_reports_list(self):
        self.reports_list.clear()
        if os.path.exists(REPORTS_DIR):
            for folder in sorted(os.listdir(REPORTS_DIR)):
                self.reports_list.addItem(folder)
        self.update_google_doc_button()

    def open_report(self, item):
        report_folder = os.path.join(REPORTS_DIR, item.text())
        files = os.listdir(report_folder)
        report_files = [f for f in files if f.endswith('.pdf') or f.endswith('.html') or f.endswith('.csv') or f.endswith('.txt')]
        if report_files:
            report_path = os.path.join(report_folder, report_files[0])
            try:
                os.startfile(report_path)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not open report: {e}')
        else:
            QMessageBox.information(self, 'No Report', 'No report file found in this folder.')
        self.update_google_doc_button()

    def show_admin_panel(self):
        dlg = AdminPanel(self, self.config)
        dlg.exec_()

    def show_home(self):
        self.stacked_pages.setCurrentWidget(self.home_page)

    def show_results(self):
        self.stacked_pages.setCurrentWidget(self.results_page)

    def show_compliance(self):
        self.stacked_pages.setCurrentWidget(self.compliance_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VyomFixDesktop()
    window.resize(600, 400)
    window.show()
    try:
        sys.exit(app.exec_())
    finally:
        cleanup_generated_code_files() 