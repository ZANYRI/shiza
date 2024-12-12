from dash import Dash, html, dcc, Input, Output, State
import time

# Параметры сессии
SESSION_TIMEOUT = 60  # Время бездействия до завершения сессии (в секундах)

# Глобальные переменные для пользователя
current_user = "test_user"
current_role = "admin"
session_start_time = time.time()

# Создание приложения
app = Dash(__name__, suppress_callback_exceptions=True)

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

    # Компонент для хранения времени последней активности на стороне клиента
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
    }, children=f"Пользователь: {current_user} ({current_role})")
])

# Callback для проверки активности пользователя и завершения сессии при бездействии
@app.callback(
    [Output('session-status', 'children'), Output('user-info', 'children')],
    Input('activity-checker', 'n_intervals'),
    State('last-activity-store', 'data')
)
def check_activity(n_intervals, data):
    global current_user, current_role, session_start_time

    # Получаем время последней активности из localStorage через JavaScript
    last_activity_time = float(data.get('last_activity', time.time()))

    # Проверка, истекло ли время бездействия
    if time.time() - last_activity_time > SESSION_TIMEOUT:
        current_user = None
        current_role = None
        return "Сессия завершена из-за бездействия. Перезагрузите страницу для повторной авторизации.", ""

    return "Сессия активна. Добро пожаловать!", f"Пользователь: {current_user} ({current_role})"

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
