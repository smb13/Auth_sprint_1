from sqlalchemy import Column, String
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255), unique=True, nullable=True)

    def __init__(self, login: str, password: str, first_name: str, last_name: str, email: str) -> None:
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'
