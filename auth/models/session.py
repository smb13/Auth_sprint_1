from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, UUID, DateTime
from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class Session(IdMixin, TimestampMixin, Base):
    __tablename__ = 'sessions'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    refresh_token = Column(String, nullable=False)
    expire = Column(DateTime, nullable=False)

    def __init__(
            self, user_id: str, refresh_token: str, expire: datetime
    ) -> None:
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.expire = expire

    def __repr__(self) -> str:
        return f'<Session {self.id} {self.user_id}>'
