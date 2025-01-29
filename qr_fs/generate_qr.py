import qrcode
import sqlite3

# Initialize the SQLite database and create table if it doesn't exist
def init_db():
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

# Generate a QR code for a given participant ID
def generate_qr_code(participant_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(participant_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f"qrcodes/{participant_id}.png")

# Add a participant to the database
def add_participant(participant_id):
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO participants (id, breakfast, lunch, dinner)
        VALUES (?, 0, 0, 0)
    ''', (participant_id,))
    conn.commit()
    conn.close()

# Main function to generate 325 unique QR codes
def main():
    init_db()  # Ensure the database is initialized
    for i in range(1, 326):
        participant_id = f"FOODCOUPON_{i:03d}"  # Unique IDs like FOODCOUPON_001, FOODCOUPON_002, ...
        generate_qr_code(participant_id)
        add_participant(participant_id)
        print(f"QR code generated and participant added for {participant_id}")

if __name__ == '__main__':
    import os
    os.makedirs("qrcodes", exist_ok=True)  # Create a folder to store QR codes
    main()
