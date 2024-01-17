from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = 'users'

    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    superuser = Column(Boolean(), default=False)

    def __init__(
            self, login: str, password: str, first_name: str, last_name: str, email: str, superuser: bool = False
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.superuser = superuser or False

    roles = relationship('UserRole', back_populates='user', lazy='selectin')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def update(self, login: str | None = None, password: str | None = None) -> None:
        if login:
            self.login = login
        if password:
            self.password = generate_password_hash(password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'
