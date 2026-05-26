# main.py
from flask import Flask
from controllers.routes import main_bp
from database import init_db

app = Flask(__name__)
# Секретний ключ для шифрування сесій та повідомлень flash
app.secret_key = "super_secret_key_for_architecture_project_2026"

# Реєстрація модульних маршрутів
app.register_blueprint(main_bp)

if __name__ == "__main__":
    print("Генерація та перевірка таблиць SQLite...")
    init_db()

    print("Запуск локального Flask сервера на http://127.0.0.1:5000/ ...")
    app.run(debug=True)