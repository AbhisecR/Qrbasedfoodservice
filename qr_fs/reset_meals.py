import sqlite3
import os

def reset_meals():
    # Check if the database exists
    if not os.path.exists("qrcodes.db"):
        print("❌ Database not found! Run 'generate.py' first to create QR codes.")
        return

    # Connect to the database
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()

    # Fetch count of meals before reset
    c.execute("SELECT COUNT(*) FROM participants WHERE breakfast = 1 OR lunch = 1 OR dinner = 1;")
    meals_scanned = c.fetchone()[0]

    if meals_scanned == 0:
        print("✅ All meal records are already reset. No changes made.")
    else:
        # Reset all meal records
        c.execute("UPDATE participants SET breakfast = 0, lunch = 0, dinner = 0;")
        conn.commit()

        # Fetch count of meals after reset (should be 0)
        c.execute("SELECT COUNT(*) FROM participants WHERE breakfast = 1 OR lunch = 1 OR dinner = 1;")
        meals_after_reset = c.fetchone()[0]

        print(f"🔄 Meal records reset successfully!")
        print(f"📊 Meals scanned before reset: {meals_scanned}")
        print(f"📊 Meals scanned after reset: {meals_after_reset} (should be 0)")

    conn.close()

if __name__ == "__main__":
    reset_meals()
