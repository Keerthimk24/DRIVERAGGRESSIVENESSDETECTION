
from app import app, db, DriverData
from datetime import datetime

with app.app_context():
    now = datetime.now()
    future_data = DriverData.query.filter(DriverData.timestamp > now).all()
    print(f"Current server time: {now}")
    print(f"Future data points found: {len(future_data)}")
    for d in future_data:
        driver = d.driver
        print(f"Future entry: {d.timestamp} - {driver.name} (ID: {driver.driver_id})")
