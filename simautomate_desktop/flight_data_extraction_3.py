
import pandas as pd
import numpy as np

# --- Generate numerical data points for the first image (df_real_flight) ---
# Data points are estimated by visually inspecting the graph.
# Time points at intervals of 0.5 seconds.
time_real = np.array([
    0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
    5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0
])

x_real = np.array([
    1.0, 1.0, 0.9, 0.8, 0.7, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9,
    0.8, 0.7, 0.6, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1
])

y_real = np.array([
    1.5, 1.4, 1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0, -0.2, -0.4,
    -0.6, -0.8, -0.9, -1.0, -1.0, -0.9, -0.8, -0.7, -0.6, -0.5
])

z_real = np.array([
    -2.0, -1.8, -1.6, -1.5, -1.4, -1.4, -1.5, -1.6, -1.7, -1.8, -1.9,
    -2.0, -1.9, -1.8, -1.7, -1.6, -1.5, -1.6, -1.7, -1.8, -1.8
])

tot_real = np.array([
    2.2, 2.0, 1.8, 1.7, 1.7, 1.8, 1.8, 1.9, 2.0, 2.1, 2.2,
    2.2, 2.1, 2.0, 1.9, 1.8, 1.8, 1.9, 2.0, 2.1, 2.2
])

# Create the df_real_flight dataframe
df_real_flight = pd.DataFrame({
    'Time': time_real,
    'x': x_real,
    'y': y_real,
    'z': z_real,
    'Tot': tot_real
})

# --- Generate numerical data points for the second image (df_simulated_flight) ---
# The simulated data appears highly periodic and can be approximated with sinusoidal functions.
# Generate time points over the range 0 to 200 seconds with a small step for smooth curves.
time_simulated = np.arange(0, 200.1, 0.1)

# Common period and angular frequency for x, y, z components
period = 5.0 # seconds, estimated from graph
omega = 2 * np.pi / period

# Parameters for x (black line): A * sin(omega * t) + C
A_x = 0.5
C_x = 0.7
x_simulated = A_x * np.sin(omega * time_simulated) + C_x

# Parameters for y (red line): A * cos(omega * t) + C (starts at peak)
A_y = 0.5
C_y = 0.7
y_simulated = A_y * np.cos(omega * time_simulated) + C_y

# Parameters for z (blue line): A * sin(omega * t) + C (starts at mean, then increases)
A_z = 0.5
C_z = -1.5
z_simulated = A_z * np.sin(omega * time_simulated) + C_z

# Parameters for Tot (cyan line): Appears as a constant with small, high-frequency oscillations
# Use a smaller amplitude and double the frequency of other components for the ripple effect.
A_tot = 0.05 # Small amplitude for oscillation
C_tot = 2.25 # Mean value
omega_tot = 2 * omega # Double frequency for faster ripple
tot_simulated = A_tot * np.sin(omega_tot * time_simulated) + C_tot

# Create the df_simulated_flight dataframe
df_simulated_flight = pd.DataFrame({
    'Time': time_simulated,
    'x': x_simulated,
    'y': y_simulated,
    'z': z_simulated,
    'Tot': tot_simulated
})
