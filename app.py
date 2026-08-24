from flask import Flask, render_template_string, redirect, request
import random
import datetime
import os

app = Flask(__name__)
codes_today = [] # هنخزن: [الكود, الزوج, الاتجاه, الربح, مستخدم؟ 0/1]

@app.route('/')
def home():
    # الصفحة الرئيسية للعميل يحط فيها الكود
    html = """
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>Nexora Trade</title>
    <style>body{background:#0a0a0a;color:#fff;text-align:center;font-family:Arial;padding:40px}
   .box{background:#111;padding:30px;border-radius:15px;max-width:400px;margin:auto;border:2px solid #00aaff}
    input{width:90%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#222;color:#fff;font-size:18px;text-align:center}
   .btn{background:#00aaff;color:#000;padding:12px 30px;border-radius:8px;border:none;font-weight:bold;font-size:16px;cursor:pointer}
   .ok{color:#00ff88;font-size:20px}.error{color:#ff4444;font-size:20px}</style>
    </head><body>
    <h1>Nexora Trade</h1>
    <div class="box">
    <h2>ادخل كود الصفقة</h2>
    <form action="/check_code" method="POST">
        <input type="text" name="code" placeholder="مثال: NX-12345" required>
        <button class="btn">تحقق من الكود</button>
    </form>
    {% if result %}<p class="{{ result_class }}">{{ result }}</p>{% endif %}
    </div>
    </body></html>
    """
    result = request.args.get('result')
    result_class = request.args.get('class')
    return render_template_string(html, result=result, result_class=result_class)

@app.route('/check_code', methods=['POST'])
def check_code():
    code = request.form['code'].upper()
    global codes_today

    for i, c in enumerate(codes_today):
        if c[0] == code:
            if c[4] == 0: # لو متاح
                codes_today[i][4] = 1 # خليه مستخدم
                msg = f"✅ الكود صحيح! الزوج: {c[1]} | الاتجاه: {c[2]} | الربح: {c[3]}%"
                return redirect(f"/?result={msg}&class=ok")
            else: # لو مستخدم
                msg = "❌ هذا الكود تم استخدامه من قبل"
                return redirect(f"/?result={msg}&class=error")

    msg = "❌ الكود غير صحيح"
    return redirect(f"/?result={msg}&class=error")

@app.route('/admin/create_codes')
def create_codes():
    global codes_today
    codes_today = []
    pairs = ["BTC/USDT", "ETH/USDT", "GOLD/USD", "EUR/USD"]
    for i in range(3):
        codes_today.append([
            "NX-" + str(random.randint(10000, 99999)),
            random.choice(pairs),
            random.choice(["صعود", "هبوط"]),
            85, 0
        ])
    return redirect('/admin')

@app.route('/admin')
def admin_page():
    today = datetime.date.today().strftime("%d-%m-%Y")
    rows = ""
    if codes_today:
        for i, code in enumerate(codes_today, 1):
            status = "<span style='color:lightgreen'>متاح</span>" if code[4]==0 else "<span style='color:red'>مستخدم</span>"
            rows += f"<tr><td>{i}</td><td style='color:gold'>{code[0]}</td><td>{code[1]}</td><td>{code[2]}</td><td>{code[3]}%</td><td>{status}</td></tr>"
    else:
        rows = "<tr><td colspan='6'>مفيش اكواد. دوس انشاء</td></tr>"

    html = f"""
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>لوحة الادمن</title>
    <style>body{{background:#0a0a0a;color:#fff;text-align:center;font-family:Arial;padding:20px}}
  .btn{{background:#00aaff;color:#000;padding:12px 20px;border-radius:8px;text-decoration:none;font-weight:bold}}
    table{{width:90%;margin:20px auto;border-collapse:collapse;background:#111}}
    th,td{{border:1px solid #333;padding:10px}}th{{background:#222;color:#00aaff}}</style>
    </head><body>
    <h2>اكواد صفقات يوم {today}</h2>
    <a href="/admin/create_codes" class="btn">+ انشاء 3 اكواد جديدة</a>
    <table><tr><th>#</th><th>الكود</th><th>الزوج</th><th>الاتجاه</th><th>الربح</th><th>الحالة</th></tr>
    {rows}
    </table></body></html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
