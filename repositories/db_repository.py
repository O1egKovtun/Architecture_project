# repositories/db_repository.py
import sqlite3
import json
from database import DB_NAME

class SingletonMeta(type):
    _instances: dict = {}
    def __call__(cls, *args, **kwargs):
        try:
            return cls._instances[cls]
        except KeyError:
            cls._instances[cls] = super().__call__(*args, **kwargs)
            return cls._instances[cls]

class EventRepository(metaclass=SingletonMeta):
    def get_all(self) -> list[dict]:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_by_id(self, event_id: int) -> dict | None:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def save(self, event) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        status = getattr(event, 'status', 'Активна')
        cursor.execute(
            '''INSERT INTO events (title, event_type, description, venue, date, capacity, price, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (event.title, event.event_type, event.description, event.venue,
             event.date, event.capacity, event.price, status)
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    def update_status(self, event_id: int, status: str):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET status = ? WHERE id = ?", (status, event_id))
        conn.commit()
        conn.close()

    def get_available_capacity(self, event_id: int) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT capacity FROM events WHERE id = ?", (event_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return 0
        capacity = row[0]
        cursor.execute(
            "SELECT COALESCE(SUM(tickets_count), 0) FROM bookings WHERE event_id = ? AND status != 'Скасовано'",
            (event_id,)
        )
        booked = cursor.fetchone()[0]
        conn.close()
        return capacity - booked

class BookingRepository(metaclass=SingletonMeta):
    def save(self, booking) -> int:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        status = getattr(booking, 'status', 'Підтверджено')
        cursor.execute(
            '''INSERT INTO bookings (user_id, event_id, tickets_count, total_price, status)
               VALUES (?, ?, ?, ?, ?)''',
            (booking.user_id, booking.event_id, booking.tickets_count,
             booking.total_price, status)
        )
        conn.commit()
        booking_id = cursor.lastrowid
        conn.close()
        return booking_id

    def get_by_user(self, user_id: int) -> list[dict]:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT bookings.*, events.title AS event_title, events.date AS event_date,
                      events.venue AS event_venue, events.event_type AS event_type
               FROM bookings
               JOIN events ON bookings.event_id = events.id
               WHERE bookings.user_id = ?
               ORDER BY bookings.id DESC''',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_all(self) -> list[dict]:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT bookings.*, users.name AS user_name, users.email AS user_email, events.title AS event_title
               FROM bookings
               JOIN users ON bookings.user_id = users.id
               JOIN events ON bookings.event_id = events.id
               ORDER BY bookings.id DESC'''
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_status(self, booking_id: int, status: str):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
        conn.commit()
        conn.close()

    def get_user_ids_by_event(self, event_id: int) -> list[int]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM bookings WHERE event_id = ? AND status != 'Скасовано'", (event_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

class UserRepository(metaclass=SingletonMeta):
    def save(self, name: str, email: str) -> tuple[int | None, str | None]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            user_id = cursor.lastrowid
            role = 'admin' if 'admin' in email.lower() else 'user'
        except sqlite3.IntegrityError:
            user_id, role = None, None
        conn.close()
        return user_id, role

    def get_by_email(self, email: str) -> dict | None:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_notifications(self, user_id: int) -> list[str]:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT notifications FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return []
        try:
            return json.loads(row[0] or '[]')
        except:
            return []