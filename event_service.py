from models.builder import EventDirector
from models.factory import EventBuilderFactory
from models.observer import EventNotifier, UserNotificationObserver
from repositories.db_repository import EventRepository, BookingRepository


# ==========================================
# СЕРВІС ПОДІЙ (EventService)
# Оркеструє взаємодію між патернами Builder, Factory та Observer.
# Є "серцем" бізнес-логіки для управління подіями.
# ==========================================

class EventService:
    """
    Сервіс управління подіями.
    Координує Factory (вибір будівника), Builder (побудова об'єкта Event),
    Observer (сповіщення при зміні статусу).
    """

    def __init__(self):
        self.event_repo = EventRepository()
        self.booking_repo = BookingRepository()
        self.director = EventDirector()
        # EventNotifier — суб'єкт для патерну Observer
        self.notifier = EventNotifier()

    def create_event(self, form_data: dict) -> int:
        """
        Створення нової події через Builder + Factory.
        1. Factory повертає відповідний Builder за типом.
        2. Director використовує Builder для побудови Event.
        3. Repository зберігає Event у БД.
        """
        builder_type = form_data.get('builder_type', 'conference')
        # Factory вибирає потрібний будівник
        builder = EventBuilderFactory.create_builder(builder_type)

        # Director керує побудовою
        event = self.director.construct(
            builder=builder,
            title=form_data.get('title', ''),
            description=form_data.get('description', ''),
            venue=form_data.get('venue', ''),
            date=form_data.get('date', ''),
            base_price=float(form_data.get('base_price', 100)),
            base_capacity=int(form_data.get('base_capacity', 100))
        )

        return self.event_repo.save(event)

    def get_all_events(self) -> list[dict]:
        """Отримати всі події з БД."""
        return self.event_repo.get_all()

    def get_event_with_availability(self, event_id: int) -> dict | None:
        """Отримати подію разом з кількістю вільних місць."""
        event = self.event_repo.get_by_id(event_id)
        if event:
            event['available'] = self.event_repo.get_available_capacity(event_id)
        return event

    def update_event_status(self, event_id: int, status: str):
        """
        Змінити статус події і сповістити всіх учасників (Observer).
        """
        event = self.event_repo.get_by_id(event_id)
        if not event:
            return

        self.event_repo.update_status(event_id, status)

        # Observer: знаходимо всіх, хто купив квитки на цю подію,
        # і прикріплюємо до них спостерігачів-сповіщувачів
        user_ids = self.booking_repo.get_user_ids_by_event(event_id)
        for uid in user_ids:
            self.notifier.attach(UserNotificationObserver(uid))

        # Одне повідомлення — всі підписані спостерігачі отримують сповіщення
        self.notifier.notify(event['title'], f"Статус події змінено: «{status}»")

        # Очищаємо список після масового сповіщення
        self.notifier.clear()
