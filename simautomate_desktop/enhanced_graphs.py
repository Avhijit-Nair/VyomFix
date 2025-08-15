import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class EnhancedGraphVisualizer:
    """Enhanced graph visualizer with better anomaly detection and styling"""
    
    def __init__(self):
        self.colors = {
            'primary': '#ff8c42',
            'secondary': '#ff6b35',
            'anomaly': '#ff4757',
            'background': '#0a0a0a',
            'grid': '#333333',
            'text': '#e6e6e6'
        }
    
    def create_enhanced_graphs(self, report_folder, canvas):
        """Create enhanced graphs with better anomaly visualization"""
        
        try:
            # Clear previous plots
            canvas.figure.clear()
            
            # Create 1x3 subplot layout (matching original main.py)
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            fig.patch.set_facecolor(self.colors['background'])
            for ax in axes.flat:
                ax.set_facecolor(self.colors['background'])
            
            # Define chart configurations (matching original main.py structure)
            charts = [
                {'title': 'Position (m)', 'ylabel': 'Position (m)', 'type': 'position'},
                {'title': 'Euler Angle (deg)', 'ylabel': 'Euler Angle (deg)', 'type': 'euler'},
                {'title': 'Acceleration (m/s²)', 'ylabel': 'Acceleration (m/s²)', 'type': 'acceleration'}
            ]
            
            for idx, chart in enumerate(charts):
                ax = axes[idx]  # Single row, so just use idx
                self._setup_axis_style(ax)
                
                # Load data from files
                data = self._get_flight_data(chart['type'], report_folder, idx)
                if data is None:
                    self._show_placeholder(ax, f"Chart {idx+1} data not available")
                    continue
                
                self._plot_enhanced_data(ax, data, chart)
            
            fig.tight_layout()
            canvas.draw()
            return fig
            
        except Exception as e:
            print(f"Error creating enhanced graphs: {e}")
            # Show error message on canvas
            canvas.figure.clear()
            ax = canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error loading graphs:\n{str(e)}', 
                   ha='center', va='center', fontsize=14, color=self.colors['text'],
                   transform=ax.transAxes)
            ax.axis('off')
            canvas.draw()
            return canvas.figure
    
    def _setup_axis_style(self, ax):
        """Setup dark theme styling for axis"""
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, alpha=0.2, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_color(self.colors['grid'])
            spine.set_linewidth(1)
    
    def _show_placeholder(self, ax, message):
        """Show placeholder message when data is not available"""
        ax.text(0.5, 0.5, message, 
               ha='center', va='center', fontsize=12, 
               color=self.colors['text'],
               transform=ax.transAxes)
        ax.axis('off')
    
    def _get_flight_data(self, chart_type, report_folder, chart_idx):
        """Get flight data from files"""
        real_csv = f"{report_folder}/df_chart_{chart_idx+1}_real.csv"
        sim_csv = f"{report_folder}/df_chart_{chart_idx+1}_simulated.csv"
        
        try:
            if os.path.exists(real_csv) and os.path.exists(sim_csv):
                df_real = pd.read_csv(real_csv)
                df_sim = pd.read_csv(sim_csv)
                print(f"Loaded data from: {real_csv} and {sim_csv}")
                return {'real': df_real, 'sim': df_sim, 'type': 'file'}
            else:
                print(f"Data files not found: {real_csv} or {sim_csv}")
                return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    

    
    def _plot_enhanced_data(self, ax, data, chart_config):
        """Plot enhanced data with anomaly highlighting (matching original main.py structure)"""
        
        if data['type'] == 'file':
            # Use actual file data
            df_real = data['real']
            df_sim = data['sim']
            
            # Find time column
            time_col = None
            for candidate in ['Time (s)', 'time', 't', 'Time']:
                if candidate in df_real.columns:
                    time_col = candidate
                    break
            
            if not time_col:
                self._show_placeholder(ax, "No time column found")
                return
            
            # Define colors and legends based on chart type
            chart_idx = 0  # Default to first chart type
            if 'Position' in chart_config['title']:
                chart_idx = 0
            elif 'Euler' in chart_config['title']:
                chart_idx = 1
            elif 'Acceleration' in chart_config['title']:
                chart_idx = 2
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
            
            # Plot each column
            cols = [col for col in df_real.columns if col != time_col]
            for j, col in enumerate(cols):
                color = colors[chart_idx][j % len(colors[chart_idx])]
                label = legends[chart_idx][j] if j < len(legends[chart_idx]) else col
                
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
        ax.set_title(chart_config['title'], fontsize=12, 
                    color=self.colors['text'], fontweight='bold')
        ax.set_ylabel(chart_config['ylabel'], fontsize=10, color=self.colors['text'])
        ax.set_xlabel('Time (s)', fontsize=10, color=self.colors['text'])
        
        # Add legend
        ax.legend(fontsize=8, frameon=True, 
                 facecolor='#1e293b', edgecolor=self.colors['grid'],
                 loc='best')
    
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
                              color=self.colors['anomaly'], 
                              alpha=0.4, 
                              label='Detected Anomaly')
                
                # Add anomaly markers
                anomaly_times = time_data[:min_len][anomalies]
                anomaly_values = real_data[:min_len][anomalies]
                ax.scatter(anomaly_times, anomaly_values, 
                          color=self.colors['anomaly'], 
                          s=30, alpha=0.8, zorder=5)

 