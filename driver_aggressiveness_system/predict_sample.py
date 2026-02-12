import pickle
import numpy as np

# Load the model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# Input features: Speed, Acceleration, Braking, Speeding_Percentage
features = np.array([[1, 1, 1, 1]])

# Get prediction probabilities
proba = model.predict_proba(features)[0]

# Classes: ['AGGRESSIVE', 'MODERATE', 'SAFE'] - order may vary, check model.classes_
classes = model.classes_
print("Classes:", classes)
print("Probabilities:", proba)

# Map to percentages
safe_prob = proba[list(classes).index('SAFE')] * 100
moderate_prob = proba[list(classes).index('MODERATE')] * 100
aggressive_prob = proba[list(classes).index('AGGRESSIVE')] * 100

print(f"SAFE: {safe_prob:.2f}%")
print(f"MODERATE: {moderate_prob:.2f}%")
print(f"AGGRESSIVE: {aggressive_prob:.2f}%")
