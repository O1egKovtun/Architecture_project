# models/entities.py

class Event:
    """Клас даних для Події (Event). Об'єкт, який конструює Будівник."""

    def __init__(self, title: str, event_type: str, description: str,
                 venue: str, date: str, capacity: int, price: float):
        self.title = title
        self.event_type = event_type
        self.description = description
        self.venue = venue
        self.date = date
        self.capacity = capacity
        self.price = price

    def __repr__(self):
        return (f"Event(title='{self.title}', type='{self.event_type}', "
                f"venue='{self.venue}', date='{self.date}', "
                f"capacity={self.capacity}, price={self.price} UAH)")