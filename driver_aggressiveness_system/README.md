# Driver Aggressiveness System

## Overview
The Driver Aggressiveness System is a web-based application built with Flask that uses machine learning to predict and monitor driver behavior. It classifies drivers into three categories: SAFE, MODERATE, and AGGRESSIVE based on driving metrics. The system supports two user roles: Administrators and Drivers, each with tailored dashboards and functionalities.

## Features
- **Machine Learning Model**: Random Forest Classifier trained on synthetic driving data to predict aggressiveness.
- **User Authentication**: Separate login for admins and drivers using Flask-Login.
- **Admin Dashboard**:
  - View fleet status and statistics.
  - Predict driver aggressiveness manually.
  - Generate synthetic data for testing.
  - View prediction history.
  - Add new admin users.
- **Driver Dashboard**:
  - View personal driving data and predictions.
  - Check warnings and average risk score.
- **Database**: SQLite with SQLAlchemy for storing users, driving data, and warnings.
- **Real-time Warnings**: Automatic warnings for aggressive drivers.

## Installation
1. **Prerequisites**:
   - Python 3.8+
   - Virtual environment (recommended)

2. **Clone or Download the Project**:
   - Place the `driver_aggressiveness_system` folder in your desired directory.

3. **Set Up Virtual Environment**:
   ```
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```

4. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

5. **Train the Model** (if not already done):
   ```
   python train_model.py
   ```
   This generates synthetic data, trains the model, and saves it as `model.pkl`.

6. **Run the Application**:
   ```
   python app.py
   ```
   Access at `http://127.0.0.1:5000/`

## Usage
### Default Credentials
- **Admin**: Username: `admin`, Password: `admin123`
- **Driver**: Driver ID: `D001`, Password: `password`

### Admin Workflow
1. Login at `/admin/login`.
2. Dashboard shows fleet overview, charts, and recent predictions.
3. Use `/admin/predict` to input driving metrics and get predictions.
4. View full history at `/admin/history`.
5. Generate synthetic data via `/admin/generate_synthetic` for demo purposes.

### Driver Workflow
1. Login at `/driver/login`.
2. View personal data, warnings, and average risk score.

## Model Explanation
### Training Data
- **Synthetic Generation**: 2000 samples created with features: Speed, Acceleration, Braking, Speeding Percentage.
- **Categories**:
  - SAFE: Low speed/accel/braking, low speeding %.
  - MODERATE: Medium values.
  - AGGRESSIVE: High values.

### Algorithm
- **Random Forest Classifier**: 100 estimators, trained on 80% of data.
- **Evaluation**: 95% accuracy on test set.
- **Prediction**: Takes 4 features, outputs category (SAFE/MODERATE/AGGRESSIVE).
- **Risk Score**: Calculated post-prediction (0-100 scale).

### Integration
- Model loaded in `app.py` for real-time predictions.
- Predictions saved to database with timestamps.

## Database Schema
- **Admin**: id, username, password
- **Driver**: id, name, driver_id, password
- **DriverData**: id, driver_id, speed, acceleration, braking, speeding_pct, prediction, risk_score, timestamp
- **Warning**: id, driver_id, message, timestamp, is_read

## Routes
- `/`: Home page
- `/admin/login`: Admin login
- `/admin/dashboard`: Admin dashboard
- `/admin/add_admin`: Add new admin
- `/admin/history`: View all predictions
- `/admin/predict`: Manual prediction
- `/admin/generate_synthetic`: Generate demo data
- `/driver/login`: Driver login
- `/driver/dashboard`: Driver dashboard
- `/logout`: Logout

## Technologies Used
- **Backend**: Flask, SQLAlchemy, Flask-Login
- **ML**: Scikit-learn, Pandas, NumPy
- **Frontend**: HTML templates with Bootstrap (assumed via static files)
- **Database**: SQLite

## Security Notes
- Passwords are stored in plain text (use hashing in production).
- Change SECRET_KEY in production.
- Use HTTPS in production.

## Future Enhancements
- Real-time data integration from vehicles.
- More advanced ML models (e.g., neural networks).
- Email/SMS notifications for warnings.
- User registration for drivers.

## Troubleshooting
- **Model not found**: Run `train_model.py` first.
- **Database issues**: Delete `instance/database.db` and restart app to recreate.
- **Login issues**: Check session and role in browser.

For questions, refer to the code comments in `app.py` and `train_model.py`.
