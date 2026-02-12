from app import app, db, Driver
import random

first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

with app.app_context():
    print("Starting bulk driver generation...")
    
    # We'll try to add 1000 drivers. 
    # To avoid unique constraint errors, we'll check or catch exceptions, 
    # but strictly generating predictable IDs (D1000+) is safer if we know the current state.
    # However, user wants "some 1000 drivers", implying total or additional.
    # Let's target a Total of 1000.
    
    existing = Driver.query.count()
    if existing >= 1000:
        print(f"Already have {existing} drivers. No need to generate more.")
    else:
        needed = 1000 - existing
        print(f"Generating {needed} new drivers...")
        
        batch = []
        # Start ID generation from a safe offset to likely avoid conflicts with D001-D006
        start_index = existing + 100 
        
        for i in range(needed):
            idx = start_index + i
            # Create a semi-realistic name
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            
            driver_id = f"D{idx:05d}" # e.g., D00100
            
            # Simple password for everyone
            d = Driver(name=name, driver_id=driver_id, password="password")
            batch.append(d)
            
            if len(batch) >= 100:
                db.session.add_all(batch)
                db.session.commit()
                batch = []
                print(f"Generated {i+1}/{needed}")
                
        if batch:
            db.session.add_all(batch)
            db.session.commit()
            
        print("Successfully seeded drivers.")
