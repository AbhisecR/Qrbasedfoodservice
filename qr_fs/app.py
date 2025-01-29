import sqlite3
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

print("Initializing the app...")

# Initialize the SQLite database
def init_db():
    print("Initializing the database...")
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id TEXT PRIMARY KEY,
            breakfast BOOLEAN DEFAULT 0,
            lunch BOOLEAN DEFAULT 0,
            dinner BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

# User setup for demo
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

users = {
    'admin': User('1', 'admin', bcrypt.generate_password_hash('Virus').decode('utf-8'))
}

@login_manager.user_loader
def load_user(user_id):
    return users.get('admin') if user_id == '1' else None

@app.route('/')
def index():
    logging.info("Index route accessed")
    if current_user.is_authenticated:
        return redirect(url_for('scan_page'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('scan_page'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/scan')
@login_required
def scan_page():
    return render_template('scanner.html')

# Determine the current meal
def get_current_meal():
    now = datetime.now().time()
    if datetime.strptime('06:00:00', '%H:%M:%S').time() <= now < datetime.strptime('10:00:00', '%H:%M:%S').time():
        return 'breakfast'
    elif datetime.strptime('14:00:00', '%H:%M:%S').time() <= now < datetime.strptime('20:00:00', '%H:%M:%S').time():
        return 'lunch'
    elif datetime.strptime('18:00:00', '%H:%M:%S').time() <= now < datetime.strptime('22:00:00', '%H:%M:%S').time():
        return 'dinner'
    else:
        return None  # Out of meal times

# Endpoint to scan QR code
@app.route('/scan_qr', methods=['POST'])
@login_required
def scan_qr():
    logging.info("Received a scan request...")
    participant_id = request.form['id']
    meal_type = get_current_meal()

    if meal_type is None:
        logging.error("Meal type is none. Scanning is only available during meal times.")
        return "❌ Scanning is only available during meal times", 400

    try:
        conn = sqlite3.connect('qrcodes.db')
        c = conn.cursor()

        # Fetch meal status for the given QR code
        c.execute(f'SELECT {meal_type} FROM participants WHERE id = ?', (participant_id,))
        result = c.fetchone()

        if result is None:
            logging.error(f"Invalid QR code: {participant_id}.")
            return "❌ Invalid QR code", 400

        # Add logging to check the value of result
        logging.info(f"Current meal status for {meal_type}: {result[0]}")

        if result[0] == 0:  # Not scanned yet for this meal
            c.execute(f'UPDATE participants SET {meal_type} = 1 WHERE id = ?', (participant_id,))
            conn.commit()  # Ensure the commit happens
            logging.info(f"QR code valid for {meal_type}, food can be served.")
            return f"✅ QR code valid for {meal_type}, food can be served", 200
        else:  # Already scanned for this meal
            logging.info(f"QR code already scanned for {meal_type}. Participant ID: {participant_id}")
            return f"❌ QR code already scanned for {meal_type}", 400

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "❌ An error occurred. Please try again.", 500

    finally:
        conn.close()



if __name__ == '__main__':
    init_db()  # Ensure database is initialized
    app.run(debug=True, host="0.0.0.0", port=5000)
