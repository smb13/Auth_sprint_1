from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base
from models.mixin import IdMixin, TimestampMixin

admin_role_name = 'admin'


class Role(IdMixin, TimestampMixin, Base):
    __tablename__ = 'roles'

    name = Column(String(255), unique=True, nullable=False)

    users = relationship('UserRole', back_populates='role', lazy='selectin')
    permissions = relationship('RolePermission', back_populates='role', lazy='selectin')

    def __repr__(self) -> str:
        return f'<Role {self.name}, permissions: {self.permissions}>'


class UserRole(IdMixin, TimestampMixin, Base):
    __tablename__ = 'user_roles'

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False)
    role_id = Column(UUID(as_uuid=True),
                     ForeignKey('roles.id', ondelete='CASCADE'),
                     nullable=False)

    role = relationship('Role', back_populates='users', lazy='selectin')
    user = relationship('User', back_populates='roles', lazy='selectin')
