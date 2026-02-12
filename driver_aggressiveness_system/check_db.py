from app import app, db, Admin, Driver

with app.app_context():
    admins = Admin.query.all()
    drivers = Driver.query.all()
    
    print("--- Admins ---")
    for a in admins:
        print(f"ID: {a.id}, Username: {a.username}, Password: {a.password}")
        
    print("\n--- Drivers ---")
    for d in drivers:
        print(f"ID: {d.id}, DriverID: {d.driver_id}, Password: {d.password}")
        
    if not admins:
        print("\nNo admins found. Creating default admin...")
        db.session.add(Admin(username='admin', password='admin123'))
        db.session.commit()
        print("Created admin/admin123")
        
    if not drivers:
        print("\nNo drivers found. Creating default driver...")
        db.session.add(Driver(name="John Doe", driver_id="D001", password="password"))
        db.session.commit()
        print("Created D001/password")
