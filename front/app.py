from dash import Dash, html, dcc, Input, Output
from flask import Flask, session
import dash_auth
import requests
from role1_page import get_layout as role1_layout
from role2_page import get_layout as role2_layout

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Создание Flask-сервера
server = Flask(__name__)
server.secret_key = 'supersecretkey'  # Необходим для использования сессий

# Создание Dash-приложения
app = Dash(__name__, server=server, suppress_callback_exceptions=True)

# Глобальные переменные для аутентификации
current_user = None
current_role = None

# Функция для аутентификации
def authenticate_user(username, password):
    try:
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return True, data.get("role"), username
        return False, None, None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False, None, None

# Функция для dash_auth
def auth_func(username, password):
    global current_user, current_role

    is_authenticated, role, user = authenticate_user(username, password)
    if is_authenticated:
        session['user'] = user
        session['role'] = role
        current_user = user
        current_role = role
        return True
    return False

# Настройка BasicAuth для Dash
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Главный layout приложения
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback для динамического отображения страниц
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    role = session.get('role')
    if role == 'role1':
        if pathname == '/role2':
            return role2_layout(role)
        return role1_layout(role)
    elif role == 'role2':
        if pathname == '/role1':
            return role1_layout(role)
        return role2_layout(role)
    else:
        return html.Div([
            html.H1("Главная страница"),
            html.P("У вас нет доступа или вы не авторизованы.")
        ])

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
