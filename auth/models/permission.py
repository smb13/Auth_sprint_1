from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin


class Permission(IdMixin, TimestampMixin, Base):
    __tablename__ = 'permissions'

    name = Column(String(255), unique=True, nullable=False)

    roles = relationship('RolePermission', back_populates='permission', lazy='selectin')

    def __repr__(self) -> str:
        return f'<Permission {self.name}>'


class RolePermission(IdMixin, TimestampMixin, Base):
    __tablename__ = 'role_permissions'

    role_id = Column(UUID(as_uuid=True),
                     ForeignKey('roles.id', ondelete='CASCADE'),
                     nullable=False)
    permission_id = Column(UUID(as_uuid=True),
                           ForeignKey('permissions.id', ondelete='CASCADE'),
                           nullable=False)

    permission = relationship('Permission', back_populates='roles', lazy='selectin')
    role = relationship('Role', back_populates='permissions', lazy='selectin')


user_management = Permission(name='USER_MANAGEMENT_PERMISSION')
role_management = Permission(name='ROLE_MANAGEMENT_PERMISSION')
general_subscriber = Permission(name='GENERAL_SUBSCRIBER_PERMISSION')
premium_subscriber = Permission(name='PREMIUM_SUBSCRIBER_PERMISSION')

permissions = [
    user_management,
    role_management,
    general_subscriber,
    premium_subscriber,
]
