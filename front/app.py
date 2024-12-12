from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_auth
import requests
import time

# URL сервера Flask для аутентификации
SERVER_URL = "http://127.0.0.1:5000/auth"

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
    global current_user, current_role, session_start_time
    is_authenticated, role, user = authenticate_user(username, password)
    if is_authenticated:
        current_user = user
        current_role = role
        return True
    return False

# Создание приложения
app = Dash(__name__, suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(app, auth_func=auth_func)

# Запуск приложения
if __name__ == "__main__":
    app.run_server(debug=True)
