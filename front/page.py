import requests
from dash import Dash, html, dcc, Input, Output, State, callback_context
from datetime import datetime, timedelta

# Базовый URL сервера Flask
SERVER_URL = "http://127.0.0.1:5000"

# Время сессии в секундах
SESSION_DURATION = 600  # 10 минут

# Функция для авторизации
def authorize_user(username, password):
    try:
        response = requests.post(f"{SERVER_URL}/auth", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("role")  # Возвращаем роль пользователя
        return None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return None

# Создание Dash-приложения
app = Dash(__name__, suppress_callback_exceptions=True)

# Макет приложения
app.layout = html.Div([
    dcc.Store(id="user-role", storage_type="session"),  # Хранение роли пользователя
    dcc.Store(id="user-name", storage_type="session"),  # Хранение имени пользователя
    dcc.Store(id="session-expiry", storage_type="session"),  # Время окончания сессии
    dcc.Interval(id="session-check", interval=30 * 1000, n_intervals=0),  # Проверка сессии каждые 30 секунд
    html.Div(id="page-content"),  # Основное содержимое
    html.Div(
        id="greeting",
        style={
            "position": "absolute",
            "top": "20px",
            "right": "20px",
            "font-size": "16px",
            "background-color": "#f0f0f0",
            "padding": "10px",
            "border-radius": "8px",
            "display": "none"  # Изначально скрыто
        }
    )
])

# Окно входа
def login_page(error_message=""):
    return html.Div(
        style={
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "height": "100vh",
            "background-color": "#f7f7f7"
        },
        children=html.Div(
            style={
                "width": "300px",
                "padding": "20px",
                "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                "background-color": "white",
                "border-radius": "8px",
                "text-align": "center"
            },
            children=[
                html.H2("Вход", style={"margin-bottom": "20px"}),
                dcc.Input(id="username", type="text", placeholder="Имя пользователя", style={"width": "100%", "margin-bottom": "10px"}),
                dcc.Input(id="password", type="password", placeholder="Пароль", style={"width": "100%", "margin-bottom": "20px"}),
                html.Button("Войти", id="login-button", style={"width": "100%", "background-color": "#007bff", "color": "white", "border": "none", "padding": "10px"}),
                html.Div(id="login-message", style={"color": "red", "margin-top": "10px", "display": "block" if error_message else "none"}, children=error_message)
            ]
        )
    )

# Главная страница после входа
def main_page():
    return html.Div(
        style={
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "height": "100vh",
            "background-color": "#eaf4fc"
        },
        children=[
            html.H1("Добро пожаловать на главную страницу!", style={"margin-bottom": "20px"}),
        ]
    )

# Логика обновления страницы
@app.callback(
    Output("page-content", "children"),
    [Input("user-role", "data"), Input("user-name", "data")]
)
def update_page(user_role, user_name):
    if user_role and user_name:
        return main_page()
    return login_page()  # Показывать страницу входа, если нет роли и имени

# Логика входа
@app.callback(
    [Output("user-role", "data"), Output("user-name", "data"), Output("session-expiry", "data"), Output("login-message", "children")],
    Input("login-button", "n_clicks"),
    [State("username", "value"), State("password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if not username or not password:
        return None, None, None, "Введите имя пользователя и пароль."

    role = authorize_user(username, password)
    if role:
        expiry_time = (datetime.now() + timedelta(seconds=SESSION_DURATION)).timestamp()
        return role, username, expiry_time, ""  # Авторизация успешна
    return None, None, None, "Неверное имя пользователя или пароль."  # Ошибка авторизации

# Логика проверки сессии
@app.callback(
    [
        Output("user-role", "clear_data"), 
        Output("user-name", "clear_data"), 
        Output("session-expiry", "clear_data"), 
        Output("greeting", "children"), 
        Output("greeting", "style")
    ],
    Input("session-check", "n_intervals"),
    [State("session-expiry", "data"), State("user-role", "data"), State("user-name", "data")],
    prevent_initial_call=True
)
def check_session(n_intervals, expiry_time, user_role, user_name):
    if not user_role or not user_name:  # Если пользователь не авторизован, очищаем данные
        return True, True, True, "", {"display": "none"}

    if expiry_time and datetime.now().timestamp() >= expiry_time:
        # Сессия истекла, очищаем все данные
        return True, True, True, "", {"display": "none"}

    greeting_text = f"Здравствуй, {user_name} ({user_role})"
    return dash.no_update, dash.no_update, dash.no_update, greeting_text, {"display": "block"}

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
