from flask import Flask
from database import init_db
from controllers.routes import main_bp

app = Flask(__name__)
app.secret_key = "eventhub_secret_key_2026"

# Реєструємо всі маршрути з папки controllers
app.register_blueprint(main_bp)

if __name__ == "__main__":
    init_db()  # Ініціалізуємо базу даних при першому запуску
    print("🎫 EventHub запущено! Відкрийте http://127.0.0.1:5000")
    app.run(debug=True)
