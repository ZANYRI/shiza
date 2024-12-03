import requests
from dash import Dash, html, dcc, Input, Output, State

# Базовый URL сервера
SERVER_URL = "http://127.0.0.1:5000"

# Функция для авторизации и получения роли
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

# Функция для выхода
def logout_user():
    try:
        response = requests.post(f"{SERVER_URL}/logout")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return True
        return False
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False

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
            html.P(f"Ваша роль: {user_role}"),
            html.Button("Выйти", id="logout-button"),
            html.Div(id="logout-message", style={"color": "green"})
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

# Объединённый callback для входа и выхода
@app.callback(
    [Output("user-role", "data"), Output("login-message", "children"), Output("logout-message", "children")],
    [Input("login-button", "n_clicks"), Input("logout-button", "n_clicks")],
    [State("username", "value"), State("password", "value")],
    prevent_initial_call=True
)
def handle_auth(login_clicks, logout_clicks, username, password):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Определяем, какой Input вызвал callback
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_input == "login-button":
        # Логика для входа
        role = authorize_user(username, password)
        if role:
            return role, "", ""  # Устанавливаем роль, очищаем сообщения
        return None, "Неверное имя пользователя или пароль.", ""
    elif triggered_input == "logout-button":
        # Логика для выхода
        if logout_user():
            return None, "", "Вы успешно вышли из системы."
        return None, "", "Ошибка при выходе."

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
