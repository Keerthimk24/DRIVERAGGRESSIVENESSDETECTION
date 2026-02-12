from app import app, db, Driver

with app.app_context():
    drivers = Driver.query.all()
    count = len(drivers)
    
    with open('all_drivers.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total Drivers Registered: {count}\n")
        f.write("="*40 + "\n")
        f.write(f"{'DriverID':<15} | {'Name':<20}\n")
        f.write("-" * 40 + "\n")
        
        for d in drivers:
            f.write(f"{d.driver_id:<15} | {d.name:<20}\n")
            
    print(f"Successfully exported {count} drivers to all_drivers.txt")
