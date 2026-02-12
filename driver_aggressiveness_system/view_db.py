from app import app, db, Driver, DriverData, Warning, Admin

with app.app_context():
    with open('db_content.log', 'w', encoding='utf-8') as f:
        f.write("="*40 + "\n")
        f.write("       DATABASE CONTENTS SUMMARY\n")
        f.write("="*40 + "\n")
        
        # 1. Admins
        admins = Admin.query.all()
        f.write(f"\n[ADMINS] Total: {len(admins)}\n")
        for a in admins:
            f.write(f" - ID: {a.id} | User: {a.username}\n")

        # 2. Drivers
        driver_count = Driver.query.count()
        f.write(f"\n[DRIVERS] Total: {driver_count}\n")
        f.write(" - First 5 drivers:\n")
        for d in Driver.query.limit(5).all():
            f.write(f"   * {d.driver_id}: {d.name}\n")

        # 3. Driver Data
        data_count = DriverData.query.count()
        f.write(f"\n[DRIVER DATA] Total Data Points: {data_count}\n")
        f.write(f"{'Time':<10} | {'DriverID':<10} | {'Speed':<8} | {'Accel':<6} | {'Brake':<6} | {'Risk':<5} | {'Pred':<10}\n")
        f.write("-" * 80 + "\n")
        
        # Show ALL data points
        for d in DriverData.query.order_by(DriverData.timestamp.desc()).all():
            f.write(f"{d.timestamp.strftime('%H:%M:%S'):<10} | {d.driver_id:<10} | {d.speed:<8} | {d.acceleration:<6} | {d.braking:<6} | {d.risk_score:<5} | {d.prediction:<10}\n")

        # 4. Warnings
        warning_count = Warning.query.count()
        f.write(f"\n[WARNINGS] Total Warnings Sent: {warning_count}\n")
        f.write(" - Last 5 warnings:\n")
        for w in Warning.query.order_by(Warning.timestamp.desc()).limit(5).all():
            f.write(f"   * Time: {w.timestamp} | To DriverID: {w.driver_id} | Msg: {w.message[:50]}...\n")
        
        f.write("\n" + "="*40 + "\n")
    print("Logged to db_content.log")
