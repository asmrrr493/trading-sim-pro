from flask import Flask, render_template_string, redirect
import random
import datetime
import os

app = Flask(__name__)

codes_today = []

@app.route('/')
def home():
    return "<h1 style='text-align:center;color:white;background:#000;padding:50px;'>Nexora Trade شغال ✅</h1>"

@app.route('/admin/create_codes')
def create_codes():
    global codes_today
    codes_today = []
    today = datetime.date.today().strftime("%Y-%m-%d")
    pairs = ["BTC/USDT", "ETH/USDT", "GOLD/USD", "EUR/USD"]
    for i in range(3):
        code = "NX-" + str(random.randint(10000, 99999))
        pair = random.choice(pairs)
        direction = random.choice(["صعود", "هبوط"])
        codes_today.append([code, pair, direction, 85, 0])
    return redirect('/admin')

@app.route('/admin')
def admin_page():
    today = datetime.date.today().strftime("%Y-%m-%d")
    html = """
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>اكواد اليوم</title>
    <style>body{background:#0a0a0a;color:#fff;text-align:center;font-family:Arial;padding:20px}
  .btn{background:#00aaff;color:#000;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:bold}
    table{width:90%;margin:20px auto;border-collapse:collapse;background:#111}
    th,td{border:1px solid #333;padding:10px}th{background:#222;color:#00aaff}
  .code{color:#ffd700;font-weight:bold;font-size:18px}.ok{color:#00ff88}</style>
    </head><body>
    <h2>اكواد صفقات يوم {{ today }}</h2>
    <a href="/admin/create_codes" class="btn">+ انشاء 3 اكواد جديدة</a>
    <table><tr><th>#</th><th>الكود</th><th>الزوج</th><th>الاتجاه</th><th>الربح</th><th>الحالة</th></tr>
    {% for code in codes %}
    <tr><td>{{ loop.index }}</td><td class="code">{{ code[0] }}</td><td>{{ code[1] }}</td><td>{{ code[2] }}</td><td>{{ code[3] }}%</td><td class="ok">متاح</td></tr>
    {% else %}<tr><td colspan="6">مفيش اكواد. دوس انشاء</td></tr>{% endfor %}
    </table></body></html>
    """
    return render_template_string(html, codes=codes_today, today=today)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
