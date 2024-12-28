import pandas as pd
import qrcode
import sqlite3

def generate_qr_code(participant_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(participant_id)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(f"{participant_id}.png")

def add_participant(participant_id):
    conn = sqlite3.connect('qrcodes.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO participants (id, breakfast, lunch, dinner) 
        VALUES (?, ?, ?, ?)
    ''', (participant_id, 0, 0, 0))
    conn.commit()
    conn.close()

def main():
    # Replace 'participants.xlsx' with the path to your Excel file
    excel_file = 'piexcel2.csv'
    # Replace 'Sheet1' with the name of the sheet containing participant IDs
    df = pd.read_csv(excel_file)
    df['unique_participant_id'] = df['Teamid'].astype(str) + '_' + df['Name']
    for participant_id in df['unique_participant_id']:
        generate_qr_code(participant_id)
        add_participant(participant_id)
        print(f"QR code generated and participant added for {participant_id}")

if __name__ == '__main__':
    main()
