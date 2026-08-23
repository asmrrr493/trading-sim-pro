from flask import Flask, render_template, request, redirect, session
import sqlite3
import random
import datetime
import os

app = Flask(__name__)
app.secret_key = 'nexora_secret_key_123456'

# ربط قاعدة البيانات
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# انشاء الجداول
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, email TEXT, password TEXT, balance REAL)''')

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

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

# صفحة الادمن لانشاء 3 اكواد
@app.route('/admin/create_codes')
def create_codes():
    today = datetime.date.today().strftime("%Y-%m-%d")
    c.execute("DELETE FROM trade_codes WHERE date!=?", (today,))

    pairs = ["BTC/USDT", "ETH/USDT", "GOLD/USD", "EUR/USD"]
    for i in range(3):
        code = "NX-" + str(random.randint(10000, 99999))
        pair = random.choice(pairs)
        direction = random.choice(["صعود", "هبوط"])
        c.execute("INSERT INTO trade_codes (code,pair,direction,profit,date) VALUES (?,?,?,?,?)",
                  (code, pair, direction, 85, today))
    conn.commit()
    return f"تم انشاء 3 اكواد لليوم {today}"

# صفحة عرض اكواد اليوم للادمن
@app.route('/admin')
def admin_page():
    today = datetime.date.today().strftime("%Y-%m-%d")
    c.execute("SELECT code,pair,direction,profit,used FROM trade_codes WHERE date=?", (today,))
    codes = c.fetchall()
    return render_template('admin.html', codes=codes, today=today)

# صفحة تفعيل الكود للعضو
@app.route('/redeem', methods=['POST'])
def redeem_code():
    user_code = request.form['code']
    today = datetime.date.today().strftime("%Y-%m-%d")

    c.execute("SELECT * FROM trade_codes WHERE code=? AND date=? AND used=0", (user_code, today))
    data = c.fetchone()

    if data:
        c.execute("UPDATE trade_codes SET used=1, used_by=? WHERE code=?", (session.get('user','guest'), user_code))
        conn.commit()
        return f"مبروك! تم تفعيل صفقة {data[2]} {data[3]} بربح {data[4]}%"
    else:
        return "الكود غلط او مستخدم او منتهي"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
