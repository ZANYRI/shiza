from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_auth
import requests
import time

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Параметры сессии
SESSION_TIMEOUT = 60  # Время бездействия до завершения сессии (в секундах)

# Глобальные переменные для пользователя
current_user = None
current_role = None
session_start_time = None

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
    global current_user, current_role, session_start_time
    is_authenticated, role, user = authenticate_user(username, password)
    if is_authenticated:
        current_user = user
        current_role = role
        session_start_time = time.time()  # Установка времени начала сессии
        return True
    return False

# Создание приложения
app = Dash(__name__, suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Макет приложения
app.layout = html.Div([
    # JavaScript для отслеживания активности пользователя
    html.Script("""
    document.addEventListener('mousemove', () => {
        localStorage.setItem('last_activity', Date.now());
    });
    document.addEventListener('keydown', () => {
        localStorage.setItem('last_activity', Date.now());
    });
    """),

    # Хранение времени последней активности
    dcc.Store(id='last-activity-store', data={'last_activity': time.time()}),

    # Интервал для регулярной проверки активности
    dcc.Interval(id='activity-checker', interval=1000, n_intervals=0),

    # Элементы интерфейса
    html.Div(id='session-status', style={
        'font-size': '20px',
        'margin': '20px'
    }, children="Сессия активна. Добро пожаловать!"),

    html.Div(id='user-info', style={
        'font-size': '18px',
        'margin': '20px'
    }, children="")
])

# Callback для проверки активности пользователя и завершения сессии при бездействии
@app.callback(
    [Output('session-status', 'children'), Output('user-info', 'children')],
    Input('activity-checker', 'n_intervals'),
    State('last-activity-store', 'data')
)
def check_activity(n_intervals, data):
    global current_user, current_role, session_start_time

    # Если пользователь не аутентифицирован
    if not current_user or not current_role:
        return "Ошибка авторизации. Перезагрузите страницу.", ""

    # Получаем время последней активности из localStorage через JavaScript
    last_activity_time = float(data.get('last_activity', time.time()))

    # Проверка, истекло ли время бездействия
    if time.time() - last_activity_time > SESSION_TIMEOUT:
        current_user = None
        current_role = None
        session_start_time = None
        return "Сессия завершена из-за бездействия. Перезагрузите страницу для повторной авторизации.", ""

    return "Сессия активна. Добро пожаловать!", f"Пользователь: {current_user} ({current_role})"

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
