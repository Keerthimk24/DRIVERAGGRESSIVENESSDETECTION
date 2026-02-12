import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

# 1. Generate Synthetic Data
def generate_synthetic_data(num_samples=1000):
    np.random.seed(42)
    
    # Features: Speed, Acceleration, Braking, Speeding Percentage
    # Safe drivers: Moderate speed, low acceleration/braking, low speeding %
    # Aggressive drivers: High speed, hard acceleration/braking, high speeding %
    # Moderate drivers: somewhere in between
    
    data = []
    
    for _ in range(num_samples):
        category = np.random.choice(['SAFE', 'MODERATE', 'AGGRESSIVE'], p=[0.4, 0.3, 0.3])
        
        if category == 'SAFE':
            speed = np.random.normal(50, 10) # mean 50, std 10
            acceleration = np.random.normal(2, 1)
            braking = np.random.normal(2, 1)
            speeding_pct = np.random.normal(5, 5)
        elif category == 'MODERATE':
            speed = np.random.normal(70, 15)
            acceleration = np.random.normal(5, 2)
            braking = np.random.normal(5, 2)
            speeding_pct = np.random.normal(20, 10)
        else: # AGGRESSIVE
            speed = np.random.normal(100, 20)
            acceleration = np.random.normal(9, 3)
            braking = np.random.normal(9, 3)
            speeding_pct = np.random.normal(60, 20)
            
        # Clip values to realistic ranges
        speed = max(0, speed)
        acceleration = max(0, acceleration)
        braking = max(0, braking)
        speeding_pct = max(0, min(100, speeding_pct))
        
        data.append([speed, acceleration, braking, speeding_pct, category])
        
    columns = ['Speed', 'Acceleration', 'Braking', 'Speeding_Percentage', 'Category']
    df = pd.DataFrame(data, columns=columns)
    return df

if __name__ == "__main__":
    print("Generating synthetic data...")
    df = generate_synthetic_data(2000)
    
    # Calculate Risk Score (Simple heuristic for ground truth generation, largely correlated with category)
    # 0 = Safe, 100 = Aggressive
    # We won't use this for training the classifier directly to predict score, 
    # but the classifier will predict Category. We can calculate score in the app.
    # Actually, let's just train to predict Category.
    
    X = df[['Speed', 'Acceleration', 'Braking', 'Speeding_Percentage']]
    y = df['Category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    print("Model Evaluation:")
    print(classification_report(y_test, y_pred))
    
    # Save the model
    with open('model.pkl', 'wb') as f:
        pickle.dump(clf, f)
        
    print("Model saved to model.pkl")
