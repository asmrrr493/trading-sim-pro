from flask import Flask, render_template, request, jsonify, session
import random, datetime, os

app = Flask(__name__)
app.secret_key = "nexora_super_secret_2026"

db = {
    "users": {"admin@nexora.com": {"name": "Admin", "pass": "admin123", "balance": 1000000, "role": "admin", "trades": []}},
    "codes": [],
    "market": {"BTC/USD": 67420, "ETH/USD": 3540, "EUR/USD": 1.085, "GOLD/USD": 2350}
}

@app.route('/')
def home():
    return render_template('index.html', market=db["market"])

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if data['email'] in db['users']: return jsonify({"status": "error", "msg": "الايميل مستخدم"})
    db['users'][data['email']] = {"name": data['name'], "pass": data['pass'], "balance": 10000, "role": "user", "trades": []}
    return jsonify({"status": "ok"})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = db['users'].get(data['email'])
    if user and user['pass'] == data['pass']:
        session['user'] = data['email']
        return jsonify({"status": "ok", "role": user['role'], "name": user['name']})
    return jsonify({"status": "error", "msg": "بيانات خطأ"})

@app.route('/api/data')
def get_data():
    if 'user' not in session: return jsonify({"status": "error"})
    user = db['users'][session['user']]
    return jsonify({"status": "ok", "user": user, "market": db['market'], "users_count": len(db['users'])})

@app.route('/api/check_code', methods=['POST'])
def check_code():
    if 'user' not in session: return jsonify({"status": "error"})
    code = request.json['code'].upper()
    user = db['users'][session['user']]
    for i, c in enumerate(db['codes']):
        if c['code'] == code:
            if c['used']: return jsonify({"status": "error", "msg": "الكود مستخدم"})
            db['codes'][i]['used'] = True
            profit = c['profit'] * 100
            user['balance'] += profit
            user['trades'].append({"date": datetime.datetime.now().strftime("%d-%m %H:%M"), "pair": c['pair'], "type": f"كود {c['signal']}", "profit": profit})
            return jsonify({"status": "ok", "msg": f"✅ مبروك ربحت {profit}$", "new_balance": user['balance']})
    return jsonify({"status": "error", "msg": "❌ كود غير صحيح"})

@app.route('/api/admin/create_codes', methods=['POST'])
def create_codes():
    if session.get('user')!= 'admin@nexora.com': return jsonify({"status": "error"})
    db['codes'] = []
    for i in range(3):
        db['codes'].append({
            "code": "NX-" + str(random.randint(10000, 99999)),
            "pair": random.choice(list(db['market'].keys())),
            "signal": random.choice(["صعود", "هبوط"]),
            "profit": random.randint(75, 95),
            "used": False
        })
    return jsonify({"status": "ok", "codes": db['codes']})

@app.route('/api/admin/set_balance', methods=['POST'])
def set_balance():
    if session.get('user')!= 'admin@nexora.com': return jsonify({"status": "error"})
    data = request.json
    if data['email'] in db['users']:
        db['users'][data['email']]['balance'] = float(data['balance'])
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"})

@app.route('/api/logout')
def logout():
    session.pop('user', None)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
