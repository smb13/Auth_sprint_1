from pydantic import EmailStr
from sqlalchemy import Column, String
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(150))
    email = Column(String(255), unique=True, nullable=False)

    def __init__(self, login: str, password: str, full_name: str, email: EmailStr) -> None:
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.full_name = full_name
        self.email = email

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'
