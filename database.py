# database.py
import sqlite3
import os

# Робимо шлях абсолютним, щоб база завжди створювалася в корені проєкту
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "architecture_project.db")


def init_db():
    """Створює таблиці в базі даних, якщо вони ще не існують."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблиця користувачів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            notifications TEXT DEFAULT '[]'
        )
    ''')

    # Таблиця подій (куди пише паттерн Builder)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT,
            venue TEXT,
            date TEXT,
            capacity INTEGER,
            price REAL,
            status TEXT DEFAULT 'Активна'
        )
    ''')

    # Таблиця бронювань квитків
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_id INTEGER,
            tickets_count INTEGER,
            total_price REAL,
            status TEXT DEFAULT 'Підтверджено',
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Базу даних успішно ініціалізовано напряму!")