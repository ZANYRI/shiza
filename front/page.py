import requests
from dash import Dash, html, dcc, Input, Output, State

# URL сервера для авторизации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Функция для авторизации и получения роли
def authorize_user(username, password):
    try:
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("role")  # Возвращаем роль пользователя
        return None
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return None

# Создаем приложение Dash
app = Dash(__name__, suppress_callback_exceptions=True)

# Начальный макет приложения
app.layout = html.Div([
    dcc.Store(id="user-role", storage_type="session"),  # Хранение роли в сессии
    html.Div(id="page-content")  # Динамическое отображение контента
])

# Логика отображения страницы в зависимости от статуса пользователя
@app.callback(
    Output("page-content", "children"),
    Input("user-role", "data")
)
def update_layout(user_role):
    if user_role:
        # Если пользователь авторизован
        return html.Div([
            html.H1("Добро пожаловать!"),
            html.P(f"Ваша роль: {user_role}")
        ])
    else:
        # Если пользователь не авторизован
        return html.Div([
            html.H1("Пожалуйста, войдите"),
            html.Label("Имя пользователя:"),
            dcc.Input(id="username", type="text"),
            html.Label("Пароль:"),
            dcc.Input(id="password", type="password"),
            html.Button("Войти", id="login-button"),
            html.Div(id="login-message", style={"color": "red"})
        ])

# Callback для обработки входа
@app.callback(
    [Output("user-role", "data"), Output("login-message", "children")],
    Input("login-button", "n_clicks"),
    [State("username", "value"), State("password", "value")],
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    # Обработка нажатия кнопки входа
    role = authorize_user(username, password)
    if role:
        return role, ""  # Сохраняем роль пользователя и очищаем сообщение об ошибке
    return None, "Неверное имя пользователя или пароль."  # Показываем сообщение об ошибке

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
