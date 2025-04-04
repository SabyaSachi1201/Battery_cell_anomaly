# -*- coding: utf-8 -*-
"""LSTM_IMPLEMENTATION_27_03_25.ipynb
"""

# Mount Google Drive
drive.mount('/content/drive')

#code number 1
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os
from google.colab import drive
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
from tensorflow.keras.callbacks import EarlyStopping


# Specify the folder path in Google Drive
folder_path = '/content/drive/MyDrive/Data_with_SoC'  # Adjust if your folder is in a different location

# List all CSV files in the folder
all_files = [f for f in os.listdir(folder_path) if f.endswith('_with_SoC.csv')]

# Load data from all files
data = []
for file in all_files:
    file_path = os.path.join(folder_path, file)
    try:
        df = pd.read_csv(file_path)
        data.append(df)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        continue

# Check if any data was loaded
if not data:
    print("Error: No data files found or loaded. Please check the folder path.")
    exit()

# Combine all dataframes
combined_df = pd.concat(data, ignore_index=True)

# Select features and target
features = ['Voltage_measured', 'Current_measured', 'Temperature_measured']
target = 'Estimated_SOC'

# Check if the required columns exist
if not all(col in combined_df.columns for col in features + [target]):
    print(f"Error: One or more required columns ({features + [target]}) not found in the combined data.")
    exit()

# Extract feature and target data
X = combined_df[features].values
y = combined_df[target].values.reshape(-1, 1)

# Scale the features and target
feature_scaler = MinMaxScaler(feature_range=(0, 1))
target_scaler = MinMaxScaler(feature_range=(0, 1))

X_scaled = feature_scaler.fit_transform(X)
y_scaled = target_scaler.fit_transform(y)

# Define a function to create sequences for LSTM
def create_sequences(data, target, n_steps):
    sequences, labels = [], []
    for i in range(len(data) - n_steps):
        seq_x = data[i : i + n_steps]
        seq_y = target[i + n_steps]
        sequences.append(seq_x)
        labels.append(seq_y)
    return np.array(sequences), np.array(labels)

# Define the number of time steps (sequence length)
n_steps = 50

# Create sequences
X_sequences, y_sequences = create_sequences(X_scaled, y_scaled, n_steps)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=42)

# Build the LSTM model with potential regularization (Dropout)
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))  # Adding a dropout layer to reduce overfitting
model.add(LSTM(units=50))
model.add(Dropout(0.2))  # Adding another dropout layer
model.add(Dense(units=1))

# Compile the model
model.compile(optimizer='adam', loss='mse')

# Implement Early Stopping
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
# monitor: Quantity to be monitored. Here, we monitor the validation loss.
# patience: Number of epochs with no improvement after which training will be stopped.
# restore_best_weights: Whether to restore model weights from the epoch with the best value of the monitored quantity.

# Train the model with Early Stopping
history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, verbose=1, callbacks=[early_stopping])

# Make predictions on the training set
y_train_pred_scaled = model.predict(X_train)
y_train_pred = target_scaler.inverse_transform(y_train_pred_scaled)
y_train_actual = target_scaler.inverse_transform(y_train)

# Evaluate the model on the training set
train_mse = mean_squared_error(y_train_actual, y_train_pred)
train_rmse = math.sqrt(train_mse)
train_mae = mean_absolute_error(y_train_actual, y_train_pred)

print("Training Set Performance:")
print(f"MSE: {train_mse:.4f}")
print(f"RMSE: {train_rmse:.4f}")
print(f"MAE: {train_mae:.4f}")

# Evaluate the model on the test set
loss = model.evaluate(X_test, y_test, verbose=0)
print(f'Mean Squared Error on Test Set (from evaluate): {loss:.4f}')

# Make predictions on the test set
y_pred_scaled = model.predict(X_test)

# Inverse transform the scaled predictions and actual values
y_pred = target_scaler.inverse_transform(y_pred_scaled)
y_actual = target_scaler.inverse_transform(y_test)

# Evaluate the model on the test set using metrics
test_mse = mean_squared_error(y_actual, y_pred)
test_rmse = math.sqrt(test_mse)
test_mae = mean_absolute_error(y_actual, y_pred)

print("\nTest Set Performance:")
print(f"MSE: {test_mse:.4f}")
print(f"RMSE: {test_rmse:.4f}")
print(f"MAE: {test_mae:.4f}")

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(y_actual, label='Actual SoC')
plt.plot(y_pred, label='Predicted SoC')
plt.xlabel('Time Steps')
plt.ylabel('State of Charge')
plt.title('LSTM Model: Actual vs. Predicted SoC')
plt.legend()
plt.grid(True)
plt.show()

# Plot training history
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Mean Squared Error')
plt.title('LSTM Training History')
plt.legend()
plt.grid(True)
plt.show()
