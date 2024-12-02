import requests
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import dash

# URL сервера для авторизации
SERVER_URL = "http://127.0.0.1:5000"

# Глобальная переменная для хранения состояния пользователя
user_info = {"username": None, "role": None}

# Создание приложения Dash
app = Dash(__name__, suppress_callback_exceptions=True)

# Макет приложения
def serve_layout():
    if user_info["username"]:
        return html.Div([
            html.H1(f"Добро пожаловать, {user_info['username']}!"),
            html.P(f"Ваша роль: {user_info['role']}"),
            html.Button('Выход', id='logout-button'),
            html.Div(id='logout-message'),
            dcc.Interval(id='session-timer', interval=1000, n_intervals=0),
            dcc.Store(id='inactive-time', data=0)
        ])
    else:
        return html.Div([
            html.H1("Вход в систему"),
            html.Label("Имя пользователя:"),
            dcc.Input(id='username', type='text'),
            html.Label("Пароль:"),
            dcc.Input(id='password', type='password'),
            html.Button('Войти', id='login-button'),
            html.Div(id='login-message')
        ])

app.layout = serve_layout

# Callback для входа
@app.callback(
    Output('login-message', 'children'),
    [Input('login-button', 'n_clicks')],
    [dash.dependencies.State('username', 'value'),
     dash.dependencies.State('password', 'value')]
)
def login(n_clicks, username, password):
    global user_info
    if n_clicks:
        response = requests.post(f"{SERVER_URL}/auth", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            user_info["username"] = username
            user_info["role"] = data["role"]
            return "Вы успешно вошли. Обновите страницу для продолжения."
        return "Ошибка входа: неверные данные."
    return ""

# Callback для выхода и завершения сессии
@app.callback(
    Output('logout-message', 'children'),
    [Input('logout-button', 'n_clicks'), Input('session-timer', 'n_intervals')],
    [dash.dependencies.State('inactive-time', 'data')]
)
def logout(n_clicks, n_intervals, inactive_time):
    global user_info
    if n_clicks or inactive_time >= 600:  # 600 секунд = 10 минут
        requests.post(f"{SERVER_URL}/logout")
        user_info.clear()
        return "Сессия завершена. Обновите страницу для входа снова."
    return ""

# Callback для увеличения времени неактивности
@app.callback(
    Output('inactive-time', 'data'),
    [Input('session-timer', 'n_intervals')],
    [dash.dependencies.State('inactive-time', 'data')]
)
def update_inactive_time(n_intervals, inactive_time):
    return (inactive_time or 0) + 1  # Если inactive_time == None, установить в 0

# Клиентский callback для сброса таймера активности
@app.clientside_callback(
    """
    function(n_intervals, data) {
        if (data === null || data === undefined) {
            data = 0;  // Инициализация, если данные не установлены
        }
        document.body.onmousemove = function() {
            DashRenderer.emit('reset_timer');
        };
        document.body.onclick = function() {
            DashRenderer.emit('reset_timer');
        };
        return 0;  // Сброс таймера
    }
    """,
    Output('inactive-time', 'data'),
    Input('session-timer', 'n_intervals'),
    dash.dependencies.State('inactive-time', 'data')
)
def reset_timer_on_activity(n_intervals, data):
    return 0

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
