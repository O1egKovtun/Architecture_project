# services/auth_service.py
from repositories.db_repository import UserRepository

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, name: str, email: str) -> tuple[int | None, str | None]:
        return self.user_repo.save(name, email)

    def login_user(self, email: str) -> dict | None:
        return self.user_repo.get_by_email(email)