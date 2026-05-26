from abc import ABC, abstractmethod
from models.entities import Event


# ==========================================
# ПАТЕРН BUILDER (Будівник)
# Розділяє конструювання складного об'єкта (Event) від його представлення.
# Дозволяє створювати різні типи подій, використовуючи однаковий процес побудови.
# ==========================================

class EventBuilder(ABC):
    """
    Абстрактний будівник. Визначає "кроки" побудови події,
    але не реалізує їх — це завдання конкретних підкласів.
    """

    def __init__(self):
        # При кожному виклику будівника — починаємо з чистого об'єкта
        self.event = Event(
            title="", event_type="", description="",
            venue="", date="", capacity=0, price=0.0
        )

    @abstractmethod
    def set_type(self):
        """Встановити тип події та базові налаштування."""
        pass

    @abstractmethod
    def set_pricing(self, base_price: float):
        """Розрахувати фінальну ціну квитка на основі базової."""
        pass

    @abstractmethod
    def set_capacity(self, base_capacity: int):
        """Встановити місткість з урахуванням особливостей типу."""
        pass

    def set_details(self, title: str, description: str, venue: str, date: str):
        """
        Спільний крок для всіх типів — заповнення текстових полів.
        Не абстрактний, бо логіка однакова для всіх підкласів.
        """
        self.event.title = title
        self.event.description = description
        self.event.venue = venue
        self.event.date = date

    def get_result(self) -> Event:
        """Повернути побудований об'єкт."""
        return self.event


class ConcertEventBuilder(EventBuilder):
    """Будівник для концертів: підвищена ціна (коефіцієнт 1.3), подвоєна місткість."""

    def set_type(self):
        self.event.event_type = "Концерт"

    def set_pricing(self, base_price: float):
        # Концерти мають додаткові витрати: звукова апаратура, сцена
        self.event.price = round(base_price * 1.3, 2)

    def set_capacity(self, base_capacity: int):
        # Концертні майданчики вміщають більше людей
        self.event.capacity = base_capacity * 2


class ConferenceEventBuilder(EventBuilder):
    """Будівник для конференцій: стандартна ціна, стандартна місткість."""

    def set_type(self):
        self.event.event_type = "Конференція"

    def set_pricing(self, base_price: float):
        self.event.price = round(base_price * 1.0, 2)

    def set_capacity(self, base_capacity: int):
        self.event.capacity = base_capacity


class WorkshopEventBuilder(EventBuilder):
    """Будівник для майстер-класів: знижена ціна (0.7), мала група (макс. 25 осіб)."""

    def set_type(self):
        self.event.event_type = "Майстер-клас"

    def set_pricing(self, base_price: float):
        # Майстер-класи дешевші, але більш персоналізовані
        self.event.price = round(base_price * 0.7, 2)

    def set_capacity(self, base_capacity: int):
        # Малі групи — важлива умова для якості майстер-класу
        self.event.capacity = min(base_capacity, 25)


class EventDirector:
    """
    Директор — оркеструє роботу будівника.
    Знає, в якому порядку викликати кроки побудови.
    Клієнтський код (сервіс) спілкується тільки з Директором,
    не знаючи деталей конкретного будівника.
    """

    def construct(self, builder: EventBuilder, title: str, description: str,
                  venue: str, date: str, base_price: float, base_capacity: int) -> Event:
        """Побудувати подію: крок за кроком викликає методи будівника."""
        builder.set_type()
        builder.set_details(title, description, venue, date)
        builder.set_pricing(base_price)
        builder.set_capacity(base_capacity)
        return builder.get_result()
