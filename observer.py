from abc import ABC, abstractmethod
import json
import sqlite3
from database import DB_NAME


# ==========================================
# ПАТЕРН OBSERVER (Спостерігач)
# Визначає залежність "один до багатьох" між об'єктами.
# Коли стан суб'єкта (EventNotifier) змінюється, всі спостерігачі
# отримують сповіщення і оновлюються автоматично.
# ==========================================

class EventObserver(ABC):
    """
    Абстрактний спостерігач.
    Всі конкретні спостерігачі повинні реалізувати метод update().
    """

    @abstractmethod
    def update(self, event_title: str, message: str):
        """Отримати сповіщення від суб'єкта."""
        pass


class UserNotificationObserver(EventObserver):
    """
    Конкретний спостерігач: зберігає сповіщення для конкретного користувача у БД.
    Кожен такий об'єкт "прикріплений" до одного user_id.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    def update(self, event_title: str, message: str):
        """
        Зберігаємо сповіщення у поле notifications (JSON-масив) у таблиці users.
        Читаємо поточний список → додаємо нове → зберігаємо назад.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT notifications FROM users WHERE id = ?", (self.user_id,))
        row = cursor.fetchone()
        if row:
            notifications = json.loads(row[0] or '[]')
            notifications.insert(0, f"[{event_title}] {message}")  # Нові — на початок
            cursor.execute(
                "UPDATE users SET notifications = ? WHERE id = ?",
                (json.dumps(notifications, ensure_ascii=False), self.user_id)
            )
            conn.commit()
        conn.close()


class EventNotifier:
    """
    Суб'єкт (Subject / Publisher) у патерні Observer.
    Зберігає список підписників і сповіщає їх при виникненні події.
    """

    def __init__(self):
        # Список активних спостерігачів
        self._observers: list[EventObserver] = []

    def attach(self, observer: EventObserver):
        """Підписати спостерігача."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: EventObserver):
        """Відписати спостерігача."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def clear(self):
        """Очистити всіх спостерігачів (після масового сповіщення)."""
        self._observers.clear()

    def notify(self, event_title: str, message: str):
        """Сповістити всіх підписаних спостерігачів."""
        for observer in self._observers:
            observer.update(event_title, message)
