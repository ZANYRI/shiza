from dash import Dash, html, dcc
import dash_auth
from flask import Flask, request, jsonify, session
import requests
from datetime import datetime

# Создаем Flask-сервер
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Для сессий

# Массив для временного хранения пользователей
users_data = []

# URL сервера для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Функция для проверки, существует ли пользователь в локальном массиве
def user_exists(username):
    for user in users_data:
        if user['username'] == username:
            return user
    return None

# Функция для аутентификации пользователя
def authenticate_user(username, password):
    # Сначала проверяем в локальном массиве
    user = user_exists(username)
    if user:
        # Если пользователь найден в локальном массиве, возвращаем его роль
        return True, user['role']
    
    # Если пользователя нет, делаем запрос к серверу для аутентификации
    try:
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # Если аутентификация успешна, сохраняем данные пользователя в массив
                users_data.append({
                    "username": username,
                    "password": password,
                    "role": data.get("role"),
                    "login_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                return True, data.get("role")
        return False, None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False, None

# Функция для auth_func в dash_auth
def auth_func(username, password):
    is_authenticated, role = authenticate_user(username, password)
    if is_authenticated:
        session['user'] = username
        session['role'] = role
        return True
    return False

# Создаем приложение Dash
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# Настройка BasicAuth для Dash
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Главная страница Dash
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Страница для role1
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    role = session.get('role')
    if role == 'role1':
        return html.Div([
            html.H1("Страница для role1"),
            html.P(f"Добро пожаловать, пользователь с ролью: {role}"),
            dcc.Link("Перейти на страницу role2", href="/role2"),
        ])
    elif role == 'role2':
        return html.Div([
            html.H1("Страница для role2"),
            html.P(f"Добро пожаловать, пользователь с ролью: {role}"),
            dcc.Link("Перейти на страницу role1", href="/role1"),
        ])
    else:
        return html.Div([
            html.H1("Авторизация"),
            dcc.Link("Перейти на страницу role1", href="/role1"),
            dcc.Link("Перейти на страницу role2", href="/role2")
        ])

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
