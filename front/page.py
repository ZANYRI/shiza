import requests
from dash import Dash, html, dcc
from dash_auth import BasicAuth
from dash.dependencies import Input, Output
import dash

# URL сервера для авторизации
SERVER_URL = "http://127.0.0.1:5000/auth"

# Глобальная переменная для хранения роли пользователя
user_role = None

# Функция для авторизации и получения роли
def authorization_function(username, password):
    global user_role
    try:
        # Отправляем запрос на сервер
        response = requests.post(SERVER_URL, json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                user_role = data["role"]  # Сохраняем роль пользователя
                return True  # Авторизация успешна
        return False  # Авторизация не пройдена
    except Exception as e:
        print(f"Ошибка подключения к серверу: {e}")
        return False

# Создаем приложение Dash с подавлением исключений
app = Dash(__name__, suppress_callback_exceptions=True)

# Используем BasicAuth с кастомной функцией
BasicAuth(app, auth_func=authorization_function)

# Макет страницы с отображением роли и кнопкой выхода
def serve_layout():
    global user_role
    if user_role is not None:
        return html.Div([
            html.H1("Привет!"),
            html.P(f"Ваша роль: {user_role}"),
            html.Button('Выход', id='logout-button'),
            html.Div(id='logout-message')
        ])
    else:
        return html.Div([
            html.H1("Привет!"),
            html.Label("Username:"),
            dcc.Input(id='username', type='text'),
            html.Label("Password:"),
            dcc.Input(id='password', type='password'),
            html.Button('Log in', id='login-button'),
            html.Div(id='login-message')
        ])

app.layout = serve_layout

# Обработчик для выхода и входа (объединены в одном callback)
@app.callback(
    [Output('logout-message', 'children'),
     Output('logout-button', 'style'),
     Output('login-message', 'children'),
     Output('username', 'value'),
     Output('password', 'value')],
    [Input('logout-button', 'n_clicks'),
     Input('login-button', 'n_clicks')],
    [dash.dependencies.State('username', 'value'),
     dash.dependencies.State('password', 'value')]
)
def handle_login_logout(logout_clicks, login_clicks, username, password):
    global user_role
    ctx = dash.callback_context

    if not ctx.triggered:
        return "", {'display': 'block'}, "", username, password

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'logout-button' and logout_clicks:
        user_role = None  # Сбрасываем роль при выходе
        return "Вы успешно вышли.", {'display': 'none'}, "Пожалуйста, войдите снова.", "", ""
    
    if button_id == 'login-button' and login_clicks:
        if authorization_function(username, password):
            return "", {'display': 'block'}, f"Вы вошли как {username}. Ваша роль: {user_role}", "", ""
        else:
            return "", {'display': 'block'}, "Неверные данные для входа!", username, password

    return "", {'display': 'block'}, "", username, password

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
