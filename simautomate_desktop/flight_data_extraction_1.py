
import pandas as pd
import numpy as np

# Generate numerical data points for the first image (real flight data)
# The lines appear linear, so we can determine their equations from start and end points.
# Time range: 0 to 10 seconds.
# Position range: 0 to 140 meters.

# Northing (blue line): Starts at (0, 140), ends at (10, 0)
# Slope = (0 - 140) / (10 - 0) = -14
# Equation: Northing = -14 * Time + 140

# Easting (red line): Starts at (0, 112), ends at (10, 0) (visually estimated initial point)
# Slope = (0 - 112) / (10 - 0) = -11.2
# Equation: Easting = -11.2 * Time + 112

# Altitude (black line): Starts at (0, 56), ends at (10, 0) (visually estimated initial point)
# Slope = (0 - 56) / (10 - 0) = -5.6
# Equation: Altitude = -5.6 * Time + 56

time_real = np.arange(0, 10.1, 1.0) # Time points from 0 to 10 seconds, with 1-second steps
northing_real = -14.0 * time_real + 140.0
easting_real = -11.2 * time_real + 112.0
altitude_real = -5.6 * time_real + 56.0

# Create the first dataframe for real flight data
data_real = {
    'Time (s)': time_real,
    'Norting (m)': northing_real,
    'Easting (m)': easting_real,
    'Altitude (m)': altitude_real
}
df_real_flight = pd.DataFrame(data_real)

# Generate numerical data points for the second image (simulated flight data)
# The lines also appear linear.
# Time range: 0 to 200 seconds.
# Position range: 0 to 140 meters.

# Northing (blue line): Starts at (0, 140), ends at (200, 0)
# Slope = (0 - 140) / (200 - 0) = -0.7
# Equation: Northing = -0.7 * Time + 140

# Easting (red line): Starts at (0, 112), ends at (200, 0) (same initial point as real flight)
# Slope = (0 - 112) / (200 - 0) = -0.56
# Equation: Easting = -0.56 * Time + 112

# Altitude (black line): Starts at (0, 56), ends at (200, 0) (same initial point as real flight)
# Slope = (0 - 56) / (200 - 0) = -0.28
# Equation: Altitude = -0.28 * Time + 56

time_simulated = np.arange(0, 200.1, 10.0) # Time points from 0 to 200 seconds, with 10-second steps
northing_simulated = -0.7 * time_simulated + 140.0
easting_simulated = -0.56 * time_simulated + 112.0
altitude_simulated = -0.28 * time_simulated + 56.0

# Create the second dataframe for simulated flight data
data_simulated = {
    'Time (s)': time_simulated,
    'Norting (m)': northing_simulated,
    'Easting (m)': easting_simulated,
    'Altitude (m)': altitude_simulated
}
df_simulated_flight = pd.DataFrame(data_simulated)
