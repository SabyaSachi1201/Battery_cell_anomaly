import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

print("UNDERSTANDING THE PATTERN IN CHARGING CYCLE DATA")

# Define file path
data_folder = r"C:\Users\Sabyasachi Datta\VSCODE_Workspace\battery_model_data\Data_Chunk"
files = [os.path.join(data_folder, f) for f in os.listdir(data_folder) if f.endswith(".csv")]

# Define Type 1 features
type1_features = ["Voltage_measured", "Current_measured", "Temperature_measured", "Current_charge", "Voltage_charge","Time"]

# Lists to store data
time_data = []
temp_data = []
current_data = []
voltage_data = []
voltage_measured_data = []
current_measured_data = []

# Loop through all files
for file in files:
    df = pd.read_csv(file)
    
    # Check if file is Type 1
    if set(type1_features).issubset(df.columns):
        print(f"Processing {file} (Type 2)")
        
        # Extract relevant columns and drop NaN values
        df = df[["Temperature_measured", "Current_charge", "Voltage_charge", "Time", "Voltage_measured", "Current_measured"]].dropna()
        
        # Ensure numeric values
        df = df.apply(pd.to_numeric, errors="coerce").dropna()
        
        # Append data
        temp_data.extend(df["Temperature_measured"].values)
        time_data.extend(df["Time"].values)
        current_data.extend(df["Current_charge"].values)
        voltage_data.extend(df["Voltage_charge"].values)
        voltage_measured_data.extend(df["Voltage_measured"].values)
        current_measured_data.extend(df["Current_measured"].values)

# Convert lists to numpy arrays
time_data = np.array(time_data)  # X-axis (Time)
temp_data = np.array(temp_data)  # Y-axis (Temperature Measured)
current_data = np.array(current_data)  # Y-axis (Current Load)
voltage_data = np.array(voltage_data)  # Y-axis (Voltage Load)
voltage_measured_data = np.array(voltage_measured_data)  # Y-axis (Voltage Measured)
current_measured_data = np.array(current_measured_data)  # Y-axis (Current Measured)


## Ensure enough data points for visualization
if len(temp_data) > 10 and len(time_data) > 10:
    # Create subplots
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))
    
    axs[0].scatter(time_data, voltage_measured_data, color="blue", alpha=0.5, label="Voltage Measured")
    axs[0].scatter(time_data, voltage_data, color="red", alpha=0.5, label="Voltage Charge")
    axs[0].set_xlabel("Time")
    axs[0].set_ylabel("Voltage")
    axs[0].set_title("Voltage Measured vs. Time & Voltage Charge vs. Time")
    axs[0].legend()
    axs[0].grid(True)
    
    axs[1].scatter(time_data, current_measured_data, color="green", alpha=0.5, label="Current Measured")
    axs[1].scatter(time_data, current_data, color="purple", alpha=0.5, label="Current Charge")
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Current")
    axs[1].set_title("Current Measured vs. Time & Current Charge vs. Time")
    axs[1].legend()
    axs[1].grid(True)
    
       # Temperature vs Time
    axs[2].scatter(time_data, temp_data, color="orange", alpha=0.5, label="Temperature Measured")
    axs[2].set_xlabel("Time")
    axs[2].set_ylabel("Temperature")
    axs[2].set_title("Temperature Measured vs. Time")
    axs[2].legend()
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.show()
else:
    print("Not enough valid data for visualization.")