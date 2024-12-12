from dash import Dash, html, dcc, Input, Output, State
import dash_auth
import requests
import time

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Параметры сессии
SESSION_TIMEOUT = 300  # Время жизни сессии (в секундах)
ACTIVITY_TIMEOUT = 60  # Время бездействия до выхода из сессии (в секундах)

# Глобальные переменные для пользователя
current_user = None
current_role = None
session_start_time = None
last_activity_time = None  # Время последней активности пользователя

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

# Функция для dash_auth
def auth_func(username, password):
    global current_user, current_role, session_start_time, last_activity_time
    is_authenticated, role, user = authenticate_user(username, password)
    if is_authenticated:
        current_user = user
        current_role = role
        session_start_time = time.time()  # Установка времени начала сессии
        last_activity_time = time.time()  # Установка времени последней активности
        return True
    return False

# Создание приложения
app = Dash(__name__, suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Макет приложения
app.layout = html.Div([
    dcc.Interval(id="session-checker", interval=1000, n_intervals=0),  # Интервал для проверки сессии
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

# Функция главной страницы
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

# Callback для обновления контента
@app.callback(
    [Output("page-content", "children"), Output("greeting", "children")],
    [Input("session-checker", "n_intervals"), Input("page-content", "n_clicks")],  # Добавляем обработчик кликов
    [State("session-checker", "n_intervals")]
)
def update_page(n_intervals, n_clicks, last_interval):
    global current_user, current_role, session_start_time, last_activity_time

    # Если пользователь не аутентифицирован
    if not current_user or not current_role:
        return html.Div("Ошибка авторизации"), ""

    # Проверяем, не истекла ли сессия
    if time.time() - session_start_time > SESSION_TIMEOUT:
        current_user = None
        current_role = None
        session_start_time = None
        last_activity_time = None
        return html.Div("Ваша сессия истекла. Перезагрузите страницу для повторной авторизации."), ""

    # Если не было активности в течение времени, указанного в ACTIVITY_TIMEOUT
    if time.time() - last_activity_time > ACTIVITY_TIMEOUT:
        current_user = None
        current_role = None
        session_start_time = None
        last_activity_time = None
        return html.Div("Ваша сессия истекла из-за бездействия. Перезагрузите страницу для повторной авторизации."), ""

    # Обновляем время последней активности
    last_activity_time = time.time()

    # Время жизни сессии не истекло, показываем основную страницу
    greeting = f"Здравствуй, {current_user} ({current_role})"
    return main_page(current_user, current_role), greeting

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
