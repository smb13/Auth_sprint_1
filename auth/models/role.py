from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class Role(IdMixin, TimestampMixin, Base):
    __tablename__ = 'role'

    name = Column(String(255), unique=True, nullable=False)

    user_role = relationship('UserRole', back_populates='role', lazy='selectin')

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class UserRole(IdMixin, TimestampMixin, Base):
    __tablename__ = 'user_role'

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    role_id = Column(UUID(as_uuid=True),
                     ForeignKey('roles.id', ondelete='CASCADE'),
                     nullable=False)

    role = relationship('Role', back_populates='user', lazy='selectin')
    user = relationship('User', back_populates='role', lazy='selectin')
