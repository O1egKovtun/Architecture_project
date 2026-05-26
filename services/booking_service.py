# services/booking_service.py
from repositories.db_repository import BookingRepository, EventRepository

try:
    from models.entities import Booking
except ImportError:
    class Booking:
        def __init__(self, user_id, event_id, tickets_count, total_price, status="Підтверджено"):
            self.user_id = user_id
            self.event_id = event_id
            self.tickets_count = tickets_count
            self.total_price = total_price
            self.status = status


class BookingService:
    def __init__(self):
        self.booking_repo = BookingRepository()
        self.event_repo = EventRepository()

    def create_booking(self, user_id: int, event_id: int, tickets_count: int) -> int | str:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            return "Подію не знайдено."

        available_seats = self.event_repo.get_available_capacity(event_id)
        if tickets_count > available_seats:
            return f"Немає місць. Доступно: {available_seats}"

        total_price = round(event['price'] * tickets_count, 2)

        booking = Booking(
            user_id=user_id,
            event_id=event_id,
            tickets_count=tickets_count,
            total_price=total_price
        )
        return self.booking_repo.save(booking)

    def get_user_bookings(self, user_id: int) -> list[dict]:
        return self.booking_repo.get_by_user(user_id)

    def cancel_booking(self, booking_id: int):
        self.booking_repo.update_status(booking_id, "Скасовано")