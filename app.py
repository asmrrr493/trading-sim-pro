from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import random, datetime, os

app = Flask(__name__)
app.secret_key = "nexora_secret_key_2026"

db = {
    "users": {"admin@nexora.com": {"password": "admin123", "balance": 50000.0, "portfolio": {}, "is_admin": True}},
    "market": {"BTC": {"price": 65000, "change": 2.5}, "ETH": {"price": 3500, "change": -1.2}},
    "signals": [], "transactions": []
}

@app.before_request
def update_prices():
    for coin in db["market"]:
        db["market"][coin]["price"] *= (1 + random.uniform(-0.01, 0.01))

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    user = db["users"][session['user']]
    return render_template('index.html', market=db["market"], user=user, signals=db["signals"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        if email in db["users"] and db["users"][email]['password'] == data['password']:
            session['user'] = email
            return jsonify({"success": True})
        elif data.get('register'):
            db["users"][email] = {"password": data['password'], "balance": 10000.0, "portfolio": {}, "is_admin": False}
            session['user'] = email
            return jsonify({"success": True})
        return jsonify({"success": False})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/trade', methods=['POST'])
def trade():
    data = request.get_json()
    user = db["users"][session['user']]
    symbol, amount, type = data['symbol'], float(data['amount']), data['type']
    price = db["market"][symbol]['price']
    cost = amount * price
    if type == 'buy' and user['balance'] >= cost:
        user['balance'] -= cost
        user['portfolio'][symbol] = user['portfolio'].get(symbol, 0) + amount
    elif type == 'sell' and user['portfolio'].get(symbol, 0) >= amount:
        user['balance'] += cost
        user['portfolio'][symbol] -= amount
    else: return jsonify({"success": False})
    return jsonify({"success": True, "balance": user['balance']})

@app.route('/wallet', methods=['POST'])
def wallet():
    data = request.get_json()
    user = db["users"][session['user']]
    amount = float(data['amount'])
    if data['type'] == 'deposit': user['balance'] += amount
    elif data['type'] == 'withdraw' and user['balance'] >= amount: user['balance'] -= amount
    else: return jsonify({"success": False})
    return jsonify({"success": True, "balance": user['balance']})

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    user = db["users"][session['user']]
    if user['password'] == data['old']:
        user['password'] = data['new']
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/admin', methods=['POST'])
def admin():
    if not db["users"][session['user']].get("is_admin"): return jsonify({"success": False})
    data = request.get_json()
    if data['action'] == 'signal': db["signals"].append({"code": data['code'], "time": str(datetime.datetime.now())})
    elif data['action'] == 'set_price': db["market"][data['symbol']]['price'] = float(data['price'])
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
