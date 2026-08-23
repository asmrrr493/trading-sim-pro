from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import datetime
import os

app = Flask(__name__)
app.secret_key = 'nexora_secret_key_123456'

conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS trade_codes
             (id INTEGER PRIMARY KEY,
              code TEXT UNIQUE,
              pair TEXT,
              direction TEXT,
              profit INTEGER,
              date TEXT,
              used INTEGER DEFAULT 0,
              used_by TEXT)''')
conn.commit()

@app.route('/')
def home():
    return "<h1 style='text-align:center;color:white;background:#000;padding:50px;'>Nexora Trade شغال</h1>"

@app.route('/admin/create_codes')
def create_codes():
    today = datetime.date.today().strftime("%Y-%m-%d")
    c.execute("DELETE FROM trade_codes WHERE date!=?", (today,))

    pairs = ["BTC/USDT", "ETH/USDT", "GOLD/USD", "EUR/USD"]
    for i in range(3):
        code = "NX-" + str(random.randint(10000, 99999))
        pair = random.choice(pairs)
        direction = random.choice(["صعود", "هبوط"])
        try:
            c.execute("INSERT INTO trade_codes (code,pair,direction,profit,date) VALUES (?,?,?,?,?)",
                      (code, pair, direction, 85, today))
        except:
            pass # لو الكود مكرر يتجاهله
    conn.commit()
    return redirect('/admin')

@app.route('/admin')
def admin_page():
    today = datetime.date.today().strftime("%Y-%m-%d")
    c.execute("SELECT code,pair,direction,profit,used FROM trade_codes WHERE date=?", (today,))
    codes = c.fetchall()
    return render_template('admin.html', codes=codes, today=today)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
