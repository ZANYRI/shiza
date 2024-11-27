from flask import Flask, jsonify, request

app = Flask(__name__)

# Данные пользователей
users = [
    {"username": "user1", "password": "pass1", "role": 1},
    {"username": "user2", "password": "pass2", "role": 2}
]

# Эндпоинт для проверки авторизации
@app.route('/auth', methods=['POST'])
def authorize():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    # Проверка пользователя
    user = next((u for u in users if u["username"] == username and u["password"] == password), None)
    if user:
        return jsonify({"status": "success", "role": user["role"]})
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)
