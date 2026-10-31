from datetime import datetime

class Category:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Event:
    def __init__(self, id: int, title: str, description: str, category_id: int, date: str, time: str, location: str, max_participants: int):
        self.id = id
        self.title = title
        self.description = description
        self.category_id = category_id
        self.date = date
        self.time = time
        self.location = location
        self.max_participants = max_participants

    def is_upcoming(self) -> bool:
        try:
            event_datetime = datetime.strptime(f"{self.date} {self.time}", "%Y-%m-%d %H:%M")
            return event_datetime > datetime.now()
        except ValueError:
            return True

class User:
    def __init__(self, id: int, full_name: str, email: str):
        self.id = id
        self.full_name = full_name
        self.email = email

class Registration:
    def __init__(self, id: int, user_id: int, event_id: int, registration_date: str):
        self.id = id
        self.user_id = user_id
        self.event_id = event_id
        self.registration_date = registration_date
