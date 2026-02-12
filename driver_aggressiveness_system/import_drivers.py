import os
import random
from datetime import datetime, timedelta
from app import app, db, Driver, DriverData, Warning

def parse_drivers(file_path):
    drivers = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Skip header lines (first 4 lines based on file view)
    # Expected format: D001 | John Doe
    for line in lines:
        if '|' in line and 'DriverID' not in line and '====' not in line:
            parts = line.split('|')
            if len(parts) >= 2:
                driver_id = parts[0].strip()
                name = parts[1].strip()
                drivers.append({'driver_id': driver_id, 'name': name})
                if len(drivers) == 1:
                    print(f"Debug: First parsed driver: {driver_id} - {name}")
    print(f"Debug: Parsed {len(drivers)} drivers.")
    return drivers

def generate_synthetic_data(driver_id):
    # Generate 1-3 data points for each driver so they show up in dashboard
    num_points = random.randint(1, 3)
    data_points = []
    
    for _ in range(num_points):
        # Randomize behavior profile
        profile = random.random()
        
        if profile < 0.7: # 70% Safe
            category = 'SAFE'
            speed = random.uniform(40, 60)
            accel = random.uniform(1, 3)
            brake = random.uniform(1, 3)
            speeding = random.uniform(0, 10)
            risk = random.randint(0, 30)
        elif profile < 0.9: # 20% Moderate
            category = 'MODERATE'
            speed = random.uniform(60, 80)
            accel = random.uniform(3, 6)
            brake = random.uniform(3, 6)
            speeding = random.uniform(10, 30)
            risk = random.randint(31, 70)
        else: # 10% Aggressive
            category = 'AGGRESSIVE'
            speed = random.uniform(80, 120)
            accel = random.uniform(6, 10)
            brake = random.uniform(6, 10)
            speeding = random.uniform(30, 80)
            risk = random.randint(71, 99)
            
        data = DriverData(
            driver_id=driver_id,
            speed=round(speed, 1),
            acceleration=round(accel, 1),
            braking=round(brake, 1),
            speeding_pct=round(speeding, 1),
            prediction=category,
            risk_score=risk,
            timestamp=datetime.now() - timedelta(minutes=random.randint(0, 60))
        )
        data_points.append(data)
        
    return data_points

def main():
    print("Starting driver import...")
    file_path = 'all_drivers.txt'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    drivers_list = parse_drivers(file_path)
    print(f"Found {len(drivers_list)} drivers in file.")
    
    with app.app_context():
        # Create tables if they don't exist (just in case)
        db.create_all()
        
        added_count = 0
        data_count = 0
        
        for d_info in drivers_list:
            # Check if driver exists
            driver = Driver.query.filter_by(driver_id=d_info['driver_id']).first()
            
            if not driver:
                # Add new driver
                driver = Driver(
                    name=d_info['name'],
                    driver_id=d_info['driver_id'],
                    password='password'
                )
                db.session.add(driver)
                db.session.flush()
                added_count += 1
            
            # Generate initial data for everyone (or at least ensure they have some)
            # For this task, we just want to populate the dashboard, so let's add data.
            # To avoid duplicates if run multiple times, maybe check if they have recent data?
            # Or just add more, it's a history log.
            
            data_points = generate_synthetic_data(driver.id)
            for dp in data_points:
                db.session.add(dp)
                data_count += 1
            
            if (added_count + data_count) % 50 == 0:
                db.session.commit()
                print(f"Processed {d_info['driver_id']}...")
        
        db.session.commit()
        print(f"Import completed successfully.")
        print(f"Total Drivers Added: {added_count}")
        print(f"Total Data Points Generated: {data_count}")

if __name__ == "__main__":
    main()
