import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout, QTabWidget, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

class FlightSimulatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Flight Simulator - VyomFix')
        self.setGeometry(100, 100, 900, 700)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Parameter input fields (with defaults)
        self.param_inputs = {}
        form_layout = QFormLayout()
        default_params = {
            'Duration (s)': '10',
            'Time Step (s)': '0.1',
            'Initial Northing (m)': '140',
            'Initial Easting (m)': '108',
            'Initial Altitude (m)': '55',
        }
        for label, default in default_params.items():
            line_edit = QLineEdit(default)
            self.param_inputs[label] = line_edit
            form_layout.addRow(QLabel(label), line_edit)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.simulate_btn = QPushButton('Run Simulation')
        self.simulate_btn.clicked.connect(self.run_simulation)
        self.export_pdf_btn = QPushButton('Export PDF')
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(self.simulate_btn)
        button_layout.addWidget(self.export_pdf_btn)
        main_layout.addLayout(button_layout)

        # Tabs for plot previews (one per parameter group)
        self.tabs = QTabWidget()
        self.plot_canvases = []
        self.plot_figures = [None] * 8  # Store matplotlib figures for PDF export
        tab_names = [
            'Position (m)', 'Euler Angle (deg)', 'Acceleration (m/s²)', 'Rotation Rate (deg/s)',
            'Velocity (m/s)', 'Angle of Attack (deg)', 'Motor Parameters', 'Control Deflection (deg)'
        ]
        for i, name in enumerate(tab_names):
            tab = QWidget()
            vbox = QVBoxLayout()
            label = QLabel(f'{name} plot will appear here after simulation.')
            vbox.addWidget(label)
            tab.setLayout(vbox)
            self.tabs.addTab(tab, name)
            self.plot_canvases.append(None)
            # Disable tabs 4-8
            if i >= 3:
                self.tabs.setTabEnabled(i, False)
        main_layout.addWidget(self.tabs)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def run_simulation(self):
        # Get parameters
        try:
            duration = float(self.param_inputs['Duration (s)'].text())
            dt = float(self.param_inputs['Time Step (s)'].text())
            n0 = float(self.param_inputs['Initial Northing (m)'].text())
            e0 = float(self.param_inputs['Initial Easting (m)'].text())
            h0 = float(self.param_inputs['Initial Altitude (m)'].text())
        except Exception as e:
            QMessageBox.warning(self, 'Input Error', f'Invalid parameter: {e}')
            return
        t = np.arange(0, duration+dt, dt)
        n = len(t)

        # 1. Position (Northing, Easting, Altitude)
        northing = np.linspace(n0, 0, n)
        easting = np.linspace(e0, 0, n)
        altitude = np.linspace(h0, 0, n)

        # 2. Euler Angles (Roll, Pitch, Heading)
        roll = 5 * np.sin(0.2 * t)
        pitch = -10 + 2 * np.cos(0.2 * t)
        heading = -120 + 10 * np.sin(0.1 * t)

        # 3. Acceleration (x, y, z, Total)
        acc_x = 0.5 * np.sin(0.5 * t)
        acc_y = 1.0 * np.cos(0.5 * t)
        acc_z = -2.0 + 0.5 * np.sin(0.7 * t)
        acc_tot = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

        # 4. Rotation Rate (p, q, r)
        p = 5 * np.sin(0.3 * t)
        q = 3 * np.cos(0.3 * t)
        r = 2 * np.sin(0.4 * t)

        # 5. Velocity (u_gps, v_gps, w_gps, V_gps, V_air)
        u_gps = 20 + 0.5 * np.random.randn(n)
        v_gps = 5 + 0.2 * np.sin(0.2 * t)
        w_gps = 0.5 * np.cos(0.2 * t)
        V_gps = np.sqrt(u_gps**2 + v_gps**2 + w_gps**2)
        V_air = 20 + 1.0 * np.random.randn(n)

        # 6. Angle of Attack (alpha, beta)
        alpha = 15 + 2 * np.sin(0.2 * t)
        beta = -10 + 2 * np.cos(0.2 * t)

        # 7. Motor Parameters (Power, RPM)
        power = 100 + 5 * np.sin(0.1 * t)
        rpm = 3500 + 100 * np.cos(0.1 * t)

        # 8. Control Deflection (Aileron, Elevator, Rudder, Flap)
        aileron = 2 * np.sin(0.2 * t)
        elevator = 1 * np.cos(0.2 * t)
        rudder = 0.5 * np.sin(0.3 * t)
        flap = np.zeros(n)

        # Plotting functions for each tab
        plot_funcs = [
            lambda: self.plot_position(t, northing, easting, altitude),
            lambda: self.plot_euler(t, roll, pitch, heading),
            lambda: self.plot_acceleration(t, acc_x, acc_y, acc_z, acc_tot),
        ]
        for i, plot_func in enumerate(plot_funcs):
            fig = plot_func()
            canvas = FigureCanvas(fig)
            # Remove old widgets
            tab = self.tabs.widget(i)
            for j in reversed(range(tab.layout().count())):
                widget = tab.layout().itemAt(j).widget()
                if widget:
                    widget.setParent(None)
            tab.layout().addWidget(canvas)
            self.plot_canvases[i] = canvas
            self.plot_figures[i] = fig
        # Clear/disable the rest
        for i in range(3, 8):
            tab = self.tabs.widget(i)
            for j in reversed(range(tab.layout().count())):
                widget = tab.layout().itemAt(j).widget()
                if widget:
                    widget.setParent(None)
            label = QLabel('Disabled for demo')
            tab.layout().addWidget(label)
            self.plot_canvases[i] = None
            self.plot_figures[i] = None

    def plot_position(self, t, northing, easting, altitude):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, northing, 'b', label='Northing')
        ax.plot(t, easting, 'r', label='Easting')
        ax.plot(t, altitude, 'k', label='Altitude')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Position (m)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_euler(self, t, roll, pitch, heading):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, roll, 'k', label='φ (Roll)')
        ax.plot(t, pitch, 'r', label='θ (Pitch)')
        ax.plot(t, heading, 'b', label='ψ (Heading)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Euler Angle (deg)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_acceleration(self, t, acc_x, acc_y, acc_z, acc_tot):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, acc_x, 'k', label='x')
        ax.plot(t, acc_y, 'r', label='y')
        ax.plot(t, acc_z, 'b', label='z')
        ax.plot(t, acc_tot, color='c', label='Tot')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Acceleration (m/s²)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_rotation_rate(self, t, p, q, r):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, p, 'k', label='p')
        ax.plot(t, q, 'r', label='q')
        ax.plot(t, r, 'b', label='r')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Rotation Rate (deg/s)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_velocity(self, t, u_gps, v_gps, w_gps, V_gps, V_air):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, u_gps, 'k', label='u_gps')
        ax.plot(t, v_gps, 'r', label='v_gps')
        ax.plot(t, w_gps, 'b', label='w_gps')
        ax.plot(t, V_gps, color='c', label='V_gps')
        ax.plot(t, V_air, color='lime', label='V_air')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Velocity (m/s)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_angle_of_attack(self, t, alpha, beta):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, alpha, 'r', label='α')
        ax.plot(t, beta, 'b', label='β')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Angle of Attack (deg)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_motor_params(self, t, power, rpm):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, power, 'r', label='Power (W)')
        ax.plot(t, rpm, color='lime', label='Rotation Rate (RPM)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Motor Parameters')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_control_deflection(self, t, aileron, elevator, rudder, flap):
        fig, ax = plt.subplots(figsize=(6,4), dpi=100)
        ax.plot(t, aileron, 'k', label='Aileron')
        ax.plot(t, elevator, 'r', label='Elevator')
        ax.plot(t, rudder, 'b', label='Rudder')
        ax.plot(t, flap, color='lime', label='Flap')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Control Deflection (deg)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def export_pdf(self):
        # Check if simulation has been run
        if not any(self.plot_figures[:3]):
            QMessageBox.warning(self, 'Export Error', 'Please run the simulation first.')
            return
        # Only export the first 3 figures
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save PDF', '', 'PDF Files (*.pdf)')
        if not save_path:
            return
        c = pdf_canvas.Canvas(save_path, pagesize=A4)
        width, height = A4
        for i in range(3):
            fig = self.plot_figures[i]
            if fig is None:
                continue
            img_path = f'_temp_plot_{i}.png'
            fig.savefig(img_path, bbox_inches='tight')
            c.drawImage(ImageReader(img_path), 40, 200, width=520, height=320)
            c.showPage()
            os.remove(img_path)
        c.save()
        QMessageBox.information(self, 'Export Complete', f'PDF saved to {save_path}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlightSimulatorApp()
    window.show()
    sys.exit(app.exec_()) 