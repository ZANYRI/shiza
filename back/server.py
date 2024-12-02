from flask import Flask, jsonify, request, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Замените на ваш секретный ключ
app.permanent_session_lifetime = timedelta(minutes=10)  # Длительность сессии

# Данные пользователей
users = [
    {"username": "user1", "password": "pass1", "role": "admin"},
    {"username": "user2", "password": "pass2", "role": "user"}
]

# Эндпоинт для авторизации
@app.route('/auth', methods=['POST'])
def authorize():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400
    
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        session.permanent = True
        session['username'] = username
        session['role'] = user['role']
        return jsonify({"status": "success", "role": user["role"]})
    
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

# Эндпоинт для выхода
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})

# Эндпоинт для проверки сессии
@app.route('/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({"status": "success", "username": session['username'], "role": session['role']})
    return jsonify({"status": "error", "message": "Session expired"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)
