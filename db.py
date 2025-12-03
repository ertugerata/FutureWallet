import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "futurewallet.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # GÜNCELLENDİ: Yeni sütunlar eklendi (initial_usd, start_date)
    c.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY,
                    btc_amount REAL,
                    usdt_cash REAL,
                    initial_usd REAL,
                    start_date TEXT,
                    last_updated TIMESTAMP
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sim_date TIMESTAMP,
                    btc_price REAL,
                    simulated_price REAL,
                    total_value REAL,
                    ai_comment TEXT
                )''')
    
    # YENİ: Analiz ve Yorum Geçmişi
    c.execute('''CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT,
                    input_summary TEXT,
                    ai_response TEXT,
                    created_at TIMESTAMP
                )''')

    # Varsayılan değerler
    c.execute('SELECT count(*) FROM portfolio')
    if c.fetchone()[0] == 0:
        # Varsayılan: 0 BTC, 0 Nakit, 1000$ Başlangıç, Bugünün tarihi
        today_str = datetime.now().strftime("%Y-%m-%d")
        c.execute('''INSERT INTO portfolio (btc_amount, usdt_cash, initial_usd, start_date) 
                     VALUES (0.0, 0.0, 1000.0, ?)''', (today_str,))
        
    conn.commit()
    conn.close()

def get_portfolio():
    """Tüm portföy detaylarını çeker"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 4 veriyi de çekiyoruz
    c.execute('SELECT btc_amount, usdt_cash, initial_usd, start_date FROM portfolio WHERE id=1')
    data = c.fetchone()
    conn.close()
    return data 

def update_portfolio(btc, usdt, initial, date_str):
    """Portföyü yeni alanlarla günceller"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE portfolio 
                 SET btc_amount=?, usdt_cash=?, initial_usd=?, start_date=?, last_updated=? 
                 WHERE id=1''', 
              (btc, usdt, initial, date_str, datetime.now()))
    conn.commit()
    conn.close()

def save_simulation(current_price, sim_price, total_val, comment):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO history (sim_date, btc_price, simulated_price, total_value, ai_comment) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (datetime.now(), current_price, sim_price, total_val, comment))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM history ORDER BY sim_date DESC", conn)
    conn.close()
    return df

# --- YENİ FONKSİYONLAR ---

def save_analysis(analysis_type, input_summary, ai_response):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO analyses (analysis_type, input_summary, ai_response, created_at)
                 VALUES (?, ?, ?, ?)''',
              (analysis_type, input_summary, ai_response, datetime.now()))
    conn.commit()
    conn.close()

def get_analyses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM analyses ORDER BY created_at DESC", conn)
    conn.close()
    return df

def delete_analysis(analysis_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM analyses WHERE id=?", (analysis_id,))
    conn.commit()
    conn.close()
