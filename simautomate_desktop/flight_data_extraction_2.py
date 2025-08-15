
import pandas as pd
import numpy as np

# --- Data for Image 1: Real Flight Data (df_real_flight) ---
# Generate time points from 0 to 10 seconds with a step of 0.1 seconds
time_real = np.arange(0, 10.1, 0.1)

# Roll (varphi): Linearly interpolating from -5 degrees at 0s to 0 degrees at 10s
roll_real = np.linspace(-5.0, 0.0, len(time_real))

# Pitch (theta): Constant at -15 degrees across the duration
pitch_real = np.full_like(time_real, -15.0)

# Heading (psi): Linearly interpolating from -120 degrees at 0s to -110 degrees at 10s
heading_real = np.linspace(-120.0, -110.0, len(time_real))

# Create the DataFrame for real flight data
data_real_flight = {
    'Time (s)': time_real,
    'Roll (deg)': roll_real,
    'Pitch (deg)': pitch_real,
    'Heading (deg)': heading_real
}
df_real_flight = pd.DataFrame(data_real_flight)

# --- Data for Image 2: Simulated Flight Data (df_simulated_flight) ---
# Generate time points from 0 to 200 seconds with a step of 0.1 seconds
time_simulated = np.arange(0, 200.1, 0.1)

# Define the period and angular frequency of the oscillations
period = 50.0 # seconds, observed from the graph (e.g., peak to peak)
omega = 2 * np.pi / period # Angular frequency in radians per second

# The oscillations for Roll, Pitch, and Heading appear to be synchronized.
# They all reach a trough around t=12.5s, 62.5s, etc., and a peak around t=37.5s, 87.5s, etc.
# This pattern suggests a negative cosine function: Y(t) = -Amplitude * cos(omega * (t - t_trough)) + Mean
t_trough_offset = 12.5 # Time (s) at which the first trough occurs

# Roll (varphi) data generation
# Observed Min: -5 deg, Max: 5 deg.
# Mean: (5 + (-5)) / 2 = 0 deg
# Amplitude: (5 - (-5)) / 2 = 5 deg
roll_simulated = -5.0 * np.cos(omega * (time_simulated - t_trough_offset)) + 0.0

# Pitch (theta) data generation
# Observed Min: -17.5 deg, Max: -12.5 deg.
# Mean: (-17.5 + (-12.5)) / 2 = -15.0 deg
# Amplitude: (-12.5 - (-17.5)) / 2 = 2.5 deg
pitch_simulated = -2.5 * np.cos(omega * (time_simulated - t_trough_offset)) - 15.0

# Heading (psi) data generation
# Observed Min: -120 deg, Max: -110 deg.
# Mean: (-120 + (-110)) / 2 = -115.0 deg
# Amplitude: (-110 - (-120)) / 2 = 5.0 deg
heading_simulated = -5.0 * np.cos(omega * (time_simulated - t_trough_offset)) - 115.0

# Create the DataFrame for simulated flight data
data_simulated_flight = {
    'Time (s)': time_simulated,
    'Roll (deg)': roll_simulated,
    'Pitch (deg)': pitch_simulated,
    'Heading (deg)': heading_simulated
}
df_simulated_flight = pd.DataFrame(data_simulated_flight)
