from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID


class IdMixin(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)


class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
