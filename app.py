from flask import Flask, render_template_string, redirect, request, session
import random
import datetime
import os

app = Flask(__name__)
app.secret_key = "nexora_secret_2025"
codes_today = []

# حسابات تجريبية
users = {"admin@nexora.com": "123456", "user@test.com": "123456"}

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    # صفحة ادخال الكود
    html = """
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>Nexora Trade</title>
    <style>body{background:#0a0a0a;color:#fff;text-align:center;font-family:Arial;padding:40px}
  .box{background:#111;padding:30px;border-radius:15px;max-width:400px;margin:auto;border:2px solid #00aaff}
    input{width:90%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#222;color:#fff;font-size:18px;text-align:center}
  .btn{background:#00aaff;color:#000;padding:12px 30px;border-radius:8px;border:none;font-weight:bold;font-size:16px;cursor:pointer}
  .ok{color:#00ff88;font-size:20px}.error{color:#ff4444;font-size:20px}</style>
    </head><body>
    <h1 style="background:linear-gradient(90deg,#00aaff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent">NEXORA TRADE</h1>
    <div class="box">
    <h2>ادخل كود الصفقة</h2>
    <form action="/check_code" method="POST">
        <input type="text" name="code" placeholder="مثال: NX-12345" required>
        <button class="btn">تحقق من الكود</button>
    </form>
    <a href="/logout" style="color:#aaa">تسجيل خروج</a>
    {% if result %}<p class="{{ result_class }}">{{ result }}</p>{% endif %}
    </div></body></html>
    """
    result = request.args.get('result')
    result_class = request.args.get('class')
    return render_template_string(html, result=result, result_class=result_class)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            session['user'] = email
            return redirect('/')
    return render_template_string("""
    <!DOCTYPE html><html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>دخول</title>
    <style>body{background:#0a0a0a;color:#fff;font-family:Arial;padding:40px}
  .box{background:#111;padding:30px;border-radius:15px;max-width:400px;margin:auto;border:1px solid #333}
    input{width:95%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #333;background:#222;color:#fff}
  .btn{width:100%;background:#0066ff;color:#fff;padding:12px;border-radius:8px;border:none;font-weight:bold;font-size:16px}</style>
    </head><body>
    <div class="box">
    <h2 style="text-align:center;background:linear-gradient(90deg,#00aaff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent">NEXORA TRADE</h2>
    <h3>تسجيل الدخول</h3>
    <form method="POST">
        <input type="email" name="email" placeholder="البريد الالكتروني" required>
        <input type="password" name="password" placeholder="كلمة السر" required>
        <button class="btn">دخول</button>
    </form>
    <p style="text-align:center;color:#aaa;font-size:12px">حساب الادمن: admin@nexora.com / 123456</p>
    </div></body></html>
    """)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/check_code', methods=['POST'])
def check_code():
    code = request.form['code'].upper()
    global codes_today
    for i, c in enumerate(codes_today):
        if c[0] == code:
            if c[4] == 0:
                codes_today[i][4] = 1
                msg = f"✅ الكود صحيح! الزوج: {c[1]} | الاتجاه: {c[2]} | الربح: {c[3]}%"
                return redirect(f"/?result={msg}&class=ok")
            else:
                msg = "❌ هذا الكود تم استخدامه من قبل"
                return redirect(f"/?result={msg}&class=error")
    msg = "❌ الكود غير صحيح"
    return redirect(f"/?result={msg}&class=error")

@app.route('/admin/create_codes')
def create_codes():
    if session.get('user')!= 'admin@nexora.com': return "ممنوع"
    global codes_today
    codes_today = []
    pairs = ["BTC/USDT", "ETH/USDT", "GOLD/USD", "EUR/USD"]
    for i in range(3):
        codes_today.append(["NX-" + str(random.randint(10000, 99999)), random.choice(pairs), random.choice(["صعود", "هبوط"]), 85, 0])
    return redirect('/admin')

@app.route('/admin')
def admin_page():
    if session.get('user')!= 'admin@nexora.com': return "ممنوع"
    today = datetime.date.today().strftime("%d-%m-%Y")
    rows = ""
    if codes_today:
        for i, code in enumerate(codes_today, 1):
            status = "<span style='color:lightgreen'>متاح</span>" if code[4]==0 else "<span style='color:red'>مستخدم</span>"
            rows += f"<tr><td>{i}</td><td style='color:gold'>{code[0]}</td><td>{code[1]}</td><td>{code[2]}</td><td>{code[3]}%</td><td>{status}</td></tr>"
    return render_template_string(f"""<!DOCTYPE html><html dir="rtl"><head><meta charset="UTF-8"><title>الادمن</title>
    <style>body{{background:#0a0a0a;color:#fff;text-align:center}}.btn{{background:#00aaff;color:#000;padding:12px 20px;border-radius:8px;text-decoration:none}}
    table{{width:90%;margin:20px auto;border-collapse:collapse}} th,td{{border:1px solid #333;padding:10px}}</style></head>
    <body><h2>اكواد يوم {today}</h2><a href="/admin/create_codes" class="btn">+ انشاء 3 اكواد</a>
    <table>
