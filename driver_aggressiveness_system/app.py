from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pickle
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Change this for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home' # Redirect to home if not logged in

# Load ML Model
model_path = os.path.join(os.getcwd(), 'model.pkl')
model = None
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("Model not found. Please run train_model.py first.")

# --- Models ---
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    def get_role(self):
        return 'admin'

class Driver(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    driver_id = db.Column(db.String(50), unique=True, nullable=False) # Used as username for login
    password = db.Column(db.String(150), nullable=False)
    
    def get_role(self):
        return 'driver'

class DriverData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    speed = db.Column(db.Float, nullable=False)
    acceleration = db.Column(db.Float, nullable=False)
    braking = db.Column(db.Float, nullable=False)
    speeding_pct = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.String(20), nullable=False) # SAFE, MODERATE, AGGRESSIVE
    risk_score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)

# Helper for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # This is tricky with two tables. We handle it by storing role in session or checking both.
    # For simplicity, let's try to query Admin first, then Driver.
    # Note: IDs might clash if we are not careful.
    # A better approach for separate dashboards is using different blueprints or custom logic in routes.
    # But let's try to use session to help disambiguate.
    
    if 'role' in session:
        if session['role'] == 'admin':
            return Admin.query.get(int(user_id))
        elif session['role'] == 'driver':
            return Driver.query.get(int(user_id))
    return None

# --- Routes ---

@app.route('/')
def home():
    return render_template('home.html')

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        print(f"Login attempt: {username} | Found: {admin}")
        if admin and admin.password == password: # In prod use hashing!
            session['role'] = 'admin'
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    
    total_drivers = Driver.query.count()
    data_points = DriverData.query.all()
    total_warnings = Warning.query.count()
    
    # Calculate counts for charts
    safe_count = sum(1 for d in data_points if d.prediction == 'SAFE')
    mod_count = sum(1 for d in data_points if d.prediction == 'MODERATE')
    agg_count = sum(1 for d in data_points if d.prediction == 'AGGRESSIVE')
    
    chart_data = [safe_count, mod_count, agg_count]
    
    # Get recent predictions (last 5)
    recent_predictions = db.session.query(DriverData, Driver).join(Driver, DriverData.driver_id == Driver.id).order_by(DriverData.timestamp.desc()).limit(5).all()

    # --- Fleet Status (Latest entry for every driver) ---
    fleet_status = []
    drivers = Driver.query.all()
    for driver in drivers:
        latest_data = DriverData.query.filter_by(driver_id=driver.id).order_by(DriverData.timestamp.desc()).first()
        fleet_status.append({
            'driver': driver,
            'data': latest_data
        })
    
    # Sort by risk score descending (if data exists), then by name
    fleet_status.sort(key=lambda x: x['data'].risk_score if x['data'] else -1, reverse=True)

    return render_template('admin_dashboard.html', 
                           total_drivers=total_drivers,
                           high_risk_count=agg_count,
                           total_warnings=total_warnings,
                           chart_data=chart_data,
                           recent_predictions=recent_predictions,
                           fleet_status=fleet_status)

@app.route('/admin/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            new_admin = Admin(username=username, password=password)
            db.session.add(new_admin)
            db.session.commit()
            flash('New Admin added successfully')
            return redirect(url_for('admin_dashboard'))
    return render_template('add_admin.html')

@app.route('/admin/history')
@login_required
def view_history():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    # Fetch all history
    history = db.session.query(DriverData, Driver).join(Driver, DriverData.driver_id == Driver.id).order_by(DriverData.timestamp.desc()).all()
    return render_template('view_history.html', history=history)

@app.route('/admin/predict', methods=['GET', 'POST'])
@login_required
def predict_warn():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    prediction_result = None
    drivers = Driver.query.all()
    
    if request.method == 'POST':
        driver_id = request.form.get('driver_id')
        speed = float(request.form.get('speed'))
        acceleration = float(request.form.get('acceleration'))
        braking = float(request.form.get('braking'))
        speeding_pct = float(request.form.get('speeding_pct'))
        
        # Predict
        if model:
            features = np.array([[speed, acceleration, braking, speeding_pct]])
            pred_category = model.predict(features)[0]
            
            # Simple risk calculation
            risk_score = 0
            if pred_category == 'SAFE':
                risk_score = np.random.randint(0, 30)
            elif pred_category == 'MODERATE':
                risk_score = np.random.randint(31, 70)
            else:
                risk_score = np.random.randint(71, 100)
                
            prediction_result = {
                'category': pred_category,
                'risk_score': risk_score
            }
            
            # Save data
            new_data = DriverData(
                driver_id=driver_id,
                speed=speed,
                acceleration=acceleration,
                braking=braking,
                speeding_pct=speeding_pct,
                prediction=pred_category,
                risk_score=risk_score
            )
            db.session.add(new_data)
            
            if pred_category == 'AGGRESSIVE':
                msg = f"Warning: High Aggressiveness Detected! Speed: {speed}, Risk: {risk_score}"
                new_warning = Warning(driver_id=driver_id, message=msg)
                db.session.add(new_warning)
                flash('High Risk! Warning sent to driver automatically.', 'danger')
            else:
                flash('Prediction Result: ' + pred_category, 'info')
                
            db.session.commit()
            
    return render_template('predict.html', drivers=drivers, result=prediction_result)

@app.route('/admin/generate_synthetic')
@login_required
def generate_synthetic():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
        
    # Generate 10 random data points
    drivers = Driver.query.all()
    if not drivers:
        flash('No drivers found to associate data with.', 'warning')
        return redirect(url_for('admin_dashboard'))
        
    import random
    count = 0
    for _ in range(10):
        driver = random.choice(drivers)
        category = random.choice(['SAFE', 'MODERATE', 'AGGRESSIVE'])
        
        if category == 'SAFE':
            speed = random.uniform(40, 60)
            accel = random.uniform(1, 3)
            brake = random.uniform(1, 3)
            speeding = random.uniform(0, 10)
            risk = random.randint(0, 30)
        elif category == 'MODERATE':
            speed = random.uniform(60, 80)
            accel = random.uniform(3, 6)
            brake = random.uniform(3, 6)
            speeding = random.uniform(10, 30)
            risk = random.randint(31, 70)
        else:
            speed = random.uniform(80, 120)
            accel = random.uniform(6, 10)
            brake = random.uniform(6, 10)
            speeding = random.uniform(30, 80)
            risk = random.randint(71, 99)
            
        new_data = DriverData(
            driver_id=driver.id,
            speed=round(speed, 1),
            acceleration=round(accel, 1),
            braking=round(brake, 1),
            speeding_pct=round(speeding, 1),
            prediction=category,
            risk_score=risk,
            timestamp=datetime.now()
        )
        db.session.add(new_data)
        
        if category == 'AGGRESSIVE':
            msg = f"Automatic Warning: Excessive speed ({round(speed, 1)} km/h) detected."
            new_warning = Warning(driver_id=driver.id, message=msg, timestamp=datetime.now())
            db.session.add(new_warning)
            
        count += 1
        
    db.session.commit()
    flash(f'Successfully generated {count} synthetic data points.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    return redirect(url_for('home'))


# Driver Routes
@app.route('/driver/login', methods=['GET', 'POST'])
def driver_login():
    if request.method == 'POST':
        driver_id_str = request.form.get('driver_id')
        password = request.form.get('password')
        driver = Driver.query.filter_by(driver_id=driver_id_str).first()
        
        if driver and driver.password == password:
            session['role'] = 'driver'
            login_user(driver)
            return redirect(url_for('driver_dashboard'))
        flash('Invalid credentials')
    return render_template('driver_login.html')

@app.route('/driver/dashboard')
@login_required
def driver_dashboard():
    if session.get('role') != 'driver':
        return redirect(url_for('home'))
        
    my_data = DriverData.query.filter_by(driver_id=current_user.id).order_by(DriverData.timestamp.desc()).all()
    my_warnings = Warning.query.filter_by(driver_id=current_user.id).order_by(Warning.timestamp.desc()).all()
    
    # Calculate safety score or average risk
    avg_risk = 0
    if my_data:
        avg_risk = sum(d.risk_score for d in my_data) / len(my_data)
        
    return render_template('driver_dashboard.html', data=my_data, warnings=my_warnings, avg_risk=avg_risk)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            db.session.add(Admin(username='admin', password='admin123')) # Default credentials
            db.session.commit()
            print("Default admin created: admin/admin123")
            
        # Create a sample driver if not exists
        if not Driver.query.filter_by(driver_id='D001').first():
            db.session.add(Driver(name="John Doe", driver_id="D001", password="password"))
            db.session.commit()
            print("Default driver created: D001/password")
            
    app.run(debug=True)
