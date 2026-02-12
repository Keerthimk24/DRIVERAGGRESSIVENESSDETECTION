
from app import app, db, Driver, DriverData, Admin

with app.app_context():
    drivers = Driver.query.all()
    print(f"Total Drivers: {len(drivers)}")
    for d in drivers:
        print(f"Driver: {d.name} (ID: {d.driver_id})")

    data_count = DriverData.query.count()
    print(f"\nTotal Data Points: {data_count}")
    
    # Check whose data we have
    data_points = DriverData.query.all()
    driver_ids_with_data = set(d.driver_id for d in data_points)
    print(f"Driver DB IDs with data: {driver_ids_with_data}")
    
    # Map back to names
    for did in driver_ids_with_data:
        driver = Driver.query.get(did)
        count = DriverData.query.filter_by(driver_id=did).count()
        if driver:
            print(f"- {driver.name} ({driver.driver_id}): {count} records")
        else:
            print(f"- Unknown Driver ID {did}: {count} records")
