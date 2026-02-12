
from app import app, db, Driver, DriverData
from sqlalchemy import desc

with app.app_context():
    # Get top 20 recent predictions
    recent = db.session.query(DriverData, Driver).join(Driver, DriverData.driver_id == Driver.id).order_by(DriverData.timestamp.desc()).limit(20).all()
    
    print(f"Top 20 Recent Data Points:")
    for data, driver in recent:
        print(f"{data.timestamp} - {driver.name} ({driver.driver_id}) - {data.prediction}")
