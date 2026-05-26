from models.builder import EventDirector
from models.factory import EventBuilderFactory
from repositories.db_repository import EventRepository, BookingRepository

try:
    from models.observer import EventNotifier, UserNotificationObserver
except ImportError:
    class EventNotifier:
        def attach(self, obs): pass
        def notify(self, t, m): pass
        def clear(self): pass
    class UserNotificationObserver:
        def __init__(self, uid): pass

class EventService:
    """Сервіс управління подіями."""

    def __init__(self):
        self.event_repo = EventRepository()
        self.booking_repo = BookingRepository()
        self.director = EventDirector()
        self.notifier = EventNotifier()

    def create_event(self, form_data: dict) -> int:
        builder_type = form_data.get('builder_type', 'conference')
        builder = EventBuilderFactory.create_builder(builder_type)

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
        return self.event_repo.get_all()

    def get_event_with_availability(self, event_id: int) -> dict | None:
        event = self.event_repo.get_by_id(event_id)
        if event:
            event['available'] = self.event_repo.get_available_capacity(event_id)
        return event

    def update_event_status(self, event_id: int, status: str):
        event = self.event_repo.get_by_id(event_id)
        if not event:
            return

        self.event_repo.update_status(event_id, status)
        user_ids = self.booking_repo.get_user_ids_by_event(event_id)
        for uid in user_ids:
            self.notifier.attach(UserNotificationObserver(uid))

        self.notifier.notify(event['title'], f"Статус події змінено: «{status}»")
        self.notifier.clear()