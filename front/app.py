from dash import Dash, html, dcc, Input, Output, State
import dash_auth
import requests

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Функция проверки аутентификации
def authenticate_user(username, password):
    try:
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return True, data.get("role"), username  # Возвращаем True, роль и имя пользователя
        return False, None, None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False, None, None

# Функция аутентификации для dash_auth
def auth_func(username, password):
    is_authenticated, role, user = authenticate_user(username, password)
    if is_authenticated:
        global current_user, current_role
        current_user = user
        current_role = role
        return True
    return False

# Инициализация Dash-приложения
app = Dash(__name__, suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Глобальные переменные для хранения данных пользователя
current_user = None
current_role = None

# Макет приложения
app.layout = html.Div([
    html.Div(id="greeting", style={
        "position": "absolute",
        "top": "20px",
        "right": "20px",
        "font-size": "16px",
        "background-color": "#f0f0f0",
        "padding": "10px",
        "border-radius": "8px"
    }),
    html.Div(id="page-content")  # Основной контент
])

# Главная страница
def main_page(user_name, user_role):
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
                html.H1(f"Добро пожаловать, {user_role}!", style={"margin-bottom": "20px"}),
                html.P(f"Ваше имя: {user_name}")
            ]
        )
    )

# Логика обновления страницы
@app.callback(
    [Output("page-content", "children"), Output("greeting", "children")],
    Input("greeting", "id"),  # Используем фиктивный Input для обновления
)
def update_page(_):
    global current_user, current_role
    if current_user and current_role:
        greeting = f"Здравствуй, {current_user} ({current_role})"
        return main_page(current_user, current_role), greeting
    return html.Div("Ошибка авторизации"), ""

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
