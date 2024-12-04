import requests
from dash import Dash, html, dcc, Input, Output, State, callback_context

# Базовый URL сервера Flask
SERVER_URL = "http://127.0.0.1:5000"

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
    html.Div(id="page-content")  # Основное содержимое
])

# Окно входа
def login_page():
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
                html.Div(id="login-message", style={"color": "red", "margin-top": "10px"})
            ]
        )
    )

# Главная страница после входа
def main_page(user_role):
    return html.Div(
        style={
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "height": "100vh",
            "background-color": "#eaf4fc"
        },
        children=html.Div(
            style={
                "text-align": "center"
            },
            children=[
                html.H1(f"Добро пожаловать, {user_role}!", style={"margin-bottom": "20px"})
            ]
        )
    )

# Логика обновления страницы
@app.callback(
    Output("page-content", "children"),
    Input("user-role", "data")
)
def update_page(user_role):
    if user_role:
        return main_page(user_role)
    return login_page()

# Логика входа
@app.callback(
    [Output("user-role", "data"), Output("login-message", "children")],
    Input("login-button", "n_clicks"),
    [State("username", "value"), State("password", "value")],
    prevent_initial_call=True
)
def handle_auth(login_clicks, username, password):
    ctx = callback_context
    if not ctx.triggered:  # Если callback вызван автоматически, ничего не делаем
        raise dash.exceptions.PreventUpdate

    if username is None or password is None:  # Проверяем существование полей
        return None, ""  # Элементы еще не существуют
    if username and password:
        role = authorize_user(username, password)
        if role:
            return role, ""  # Авторизация успешна
        return None, "Неверное имя пользователя или пароль."  # Ошибка авторизации
    return None, "Введите имя пользователя и пароль."

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
