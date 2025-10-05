import numpy as np
import pandas as pd
from joblib import load

# Load model
model = load("./models_and_results/meteor_model.joblib")

# (Optional) load your scaler if you saved it too
# scaler = load("./models_and_results/meteor_scaler.joblib")

# Example new asteroid data
# Format: [diameter_min_km, diameter_max_km, miss_distance_km, relative_velocity_kph]
new_asteroid = np.array([[0.1536579294,0.3435895754,65489118.092761725,80273.3553080122]])

# Scale data if necessary
# new_asteroid_scaled = scaler.transform(new_asteroid)

# Predict hazard
print("Information for the new asteroid: ", new_asteroid)
prediction = model.predict(new_asteroid)
print(prediction)
print("⚠️ Is it hazardous?", "Yes" if prediction[0] == 1 else "No")
