import sqlite3
from datetime import datetime

# データベースの初期化
def init_db():
    conn = sqlite3.connect('temperature_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS temperature (
            date TEXT,
            time TEXT,
            temperature REAL
        )
    ''')
    conn.commit()
    conn.close()

# データベースにデータを保存
def save_to_db(timestamp: datetime, temperature: float):
    conn = sqlite3.connect('temperature_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO temperature (date, time, temperature)
        VALUES (?, ?, ?)
    ''', (timestamp.date().isoformat(), timestamp.time().isoformat(), temperature))
    conn.commit()
    conn.close()
