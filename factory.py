from models.builder import (
    EventBuilder, ConcertEventBuilder, ConferenceEventBuilder, WorkshopEventBuilder
)


# ==========================================
# ПАТЕРН FACTORY METHOD (Фабричний Метод)
# Визначає інтерфейс для створення об'єктів, але дозволяє підкласам
# вирішувати, який клас інстанціювати.
# Тут реалізовано як "Реєстр Фабрик" (Registry-based Factory)
# для підтримки принципу Open/Closed (OCP) з SOLID.
# ==========================================

class EventBuilderFactory:
    """
    Фабрика будівників подій.
    Зберігає реєстр (словник) відповідностей: тип рядка → клас будівника.
    Новий тип події можна додати через register() БЕЗ зміни коду фабрики.
    """

    # Словник-реєстр: ключ — рядковий ідентифікатор, значення — клас будівника
    _registry: dict[str, type] = {
        'concert': ConcertEventBuilder,
        'conference': ConferenceEventBuilder,
        'workshop': WorkshopEventBuilder,
    }

    @classmethod
    def register(cls, event_type: str, builder_class: type):
        """
        Динамічна реєстрація нового типу події.
        Демонстрація принципу Open/Closed: розширюємо без модифікації.
        """
        if not issubclass(builder_class, EventBuilder):
            raise TypeError(f"Клас {builder_class.__name__} повинен успадковувати EventBuilder!")
        cls._registry[event_type] = builder_class
        print(f"[Фабрика] Зареєстровано новий тип події: '{event_type}'")

    @classmethod
    def create_builder(cls, event_type: str) -> EventBuilder:
        """
        Повернути відповідний будівник за типом.
        Клієнт не знає, який саме клас буде створено.
        """
        try:
            return cls._registry[event_type]()
        except KeyError:
            raise ValueError(f"Непідтримуваний тип події: '{event_type}'. "
                             f"Доступні: {list(cls._registry.keys())}")

    @classmethod
    def get_available_types(cls) -> list[str]:
        """Повернути список зареєстрованих типів (для відображення у формі)."""
        return list(cls._registry.keys())
