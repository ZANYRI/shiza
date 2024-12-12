from dash import Dash, html, dcc, Input, Output
import dash_auth
import requests
import time

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Параметры сессии
SESSION_TIMEOUT = 300  # Время жизни сессии (в секундах)
session_start_time = None  # Время старта сессии
last_activity_time = None  # Время последней активности пользователя

# Глобальные переменные для пользователя
current_user = None
current_role = None

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
    html.Div(id="page-content", children="Добро пожаловать!")
])

# Callback для проверки активности и завершения сессии
@app.callback(
    [Output("page-content", "children"), Output("greeting", "children")],
    Input("session-checker", "n_intervals")
)
def check_session(n_intervals):
    global current_user, current_role, session_start_time, last_activity_time

    # Если пользователь не аутентифицирован
    if not current_user or not current_role:
        return "Ошибка авторизации", ""

    # Проверяем, не истекла ли сессия из-за бездействия
    if time.time() - last_activity_time > SESSION_TIMEOUT:
        # Сброс глобальных переменных для завершения аутентификации
        current_user = None
        current_role = None
        session_start_time = None
        last_activity_time = None
        # Выходим из приложения путем вызова функции auth_func с результатом False
        auth.users = {}
        return "Сессия завершена из-за бездействия. Перезагрузите страницу для повторной авторизации.", ""

    # Если сессия активна
    last_activity_time = time.time()  # Обновляем время последней активности
    greeting = f"Здравствуй, {current_user} ({current_role})"
    return "Добро пожаловать!", greeting

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
