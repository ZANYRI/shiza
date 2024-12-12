from dash import Dash, html, dcc, Input, Output, State
import dash_auth
from flask import Flask, session, request
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
        # Если пользователь найден в локальном массиве и его статус True, возвращаем его роль
        if user['status']:
            return True, user['role']
        else:
            return False, None
    
    # Если пользователя нет, делаем запрос к серверу для аутентификации
    try:
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # Если аутентификация успешна, сохраняем данные пользователя в массив с полем status=True
                users_data.append({
                    "username": username,
                    "password": password,
                    "role": data.get("role"),
                    "login_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": True  # Добавляем статус пользователя
                })
                return True, data.get("role")
        return False, None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False, None

# Функция для изменения статуса пользователя на False
def set_status_false(username):
    for user in users_data:
        if user['username'] == username:
            user['status'] = False
            print(f"Статус пользователя {username} изменен на False.")
            return True
    print(f"Пользователь {username} не найден.")
    return False

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

# Страницы для ролей с кнопкой для изменения статуса на False
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    username = session.get('user')
    role = session.get('role')

    if role == 'role1':
        return html.Div([
            html.H1("Страница для role1"),
            html.P(f"Добро пожаловать, {username}! Ваша роль: {role}"),
            html.Button("Отключить статус", id='disable-status-btn', n_clicks=0),
            html.Div(id='status-output')
        ])
    elif role == 'role2':
        return html.Div([
            html.H1("Страница для role2"),
            html.P(f"Добро пожаловать, {username}! Ваша роль: {role}"),
            html.Button("Отключить статус", id='disable-status-btn', n_clicks=0),
            html.Div(id='status-output')
        ])
    else:
        return html.Div([
            html.H1("Авторизация"),
            html.P("Пожалуйста, авторизуйтесь.")
        ])

# Callback для изменения статуса пользователя на False
@app.callback(
    Output('status-output', 'children'),
    Input('disable-status-btn', 'n_clicks'),
    State('url', 'pathname')
)
def disable_status(n_clicks, pathname):
    username = session.get('user')
    if n_clicks > 0 and username:
        if set_status_false(username):
            return f"Статус пользователя {username} был отключен."
        else:
            return "Не удалось отключить статус."
    return ""

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
