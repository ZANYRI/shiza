from dash import Dash, html, dcc, Input, Output
import dash_auth
from flask import Flask, request, jsonify, session
from datetime import datetime
import role1_page  # Импорт страницы для role1
import role2_page  # Импорт страницы для role2

# Создаем Flask-сервер
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Для сессий

# Массив для хранения данных пользователей (временное хранение)
users_data = []

# Функция для проверки, существует ли уже пользователь с таким логином и паролем
def user_exists(username, password):
    for user in users_data:
        if user['username'] == username and user['password'] == password:
            return True
    return False

# Функция для добавления пользователя
def register_user(username, password, role):
    if not user_exists(username, password):
        users_data.append({
            "username": username,
            "password": password,
            "role": role,
            "login_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return True
    return False

# Функция для проверки аутентификации
def authenticate_user(username, password):
    for user in users_data:
        if user['username'] == username and user['password'] == password:
            return True, user['role']
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
        return role1_page.get_role1_page()  # Загружаем страницу для role1
    elif role == 'role2':
        return role2_page.get_role2_page()  # Загружаем страницу для role2
    else:
        return html.Div([
            html.H1("Авторизация"),
            dcc.Link("Перейти на страницу role1", hre
