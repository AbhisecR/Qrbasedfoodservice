import sqlite3
from flask import Flask, request, render_template
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

print("Initializing the app...")

def init_db():
    print("Initializing the database...")
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id TEXT PRIMARY KEY,
            breakfast BOOLEAN,
            lunch BOOLEAN,
            dinner BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

@app.route('/')
def index():
    logging.info("Index route accessed")
    return render_template('scanner.html')

# Determine the current meal
def get_current_meal():
    now = datetime.now().time()
    if datetime.strptime('06:00:00', '%H:%M:%S').time() <= now < datetime.strptime('10:00:00', '%H:%M:%S').time():
        return 'breakfast'
    elif datetime.strptime('14:00:00', '%H:%M:%S').time() <= now < datetime.strptime('20:00:00', '%H:%M:%S').time():
        return 'lunch'
    elif datetime.strptime('18:00:00', '%H:%M:%S').time() <= now < datetime.strptime('21:00:00', '%H:%M:%S').time():
        return 'dinner'
    else:
        return None  # Out of meal times

# Endpoint to scan QR code
@app.route('/scan', methods=['POST'])
def scan_qr():
    logging.info("Received a scan request...")
    participant_id = request.form['id']
    meal_type = get_current_meal()
    
    if meal_type is None:
        return "Scanning is only available during meal times", 400

    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute(f'SELECT {meal_type} FROM participants WHERE id = ?', (participant_id,))
    result = c.fetchone()
    
    if result is None:
        return "Invalid QR code", 400
    if result[0] == 0:  # Not scanned yet for this meal
        c.execute(f'UPDATE participants SET {meal_type} = 1 WHERE id = ?', (participant_id,))
        conn.commit()
        return f"QR code valid for {meal_type}, food can be served", 200
    else:  # Already scanned for this meal
        return f"QR code already scanned for {meal_type}", 400

print("App setup complete.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True,host="0.0.0.0",port=5000)
