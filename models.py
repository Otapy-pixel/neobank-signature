import uuid
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db import Base

class User(Base):
    tablename = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    first_name = Column(String(100))
    last_name = Column(String(100))
    password_hash = Column(String(255))
    kyc_status = Column(String(20), default="pending")
    stripe_customer_id = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

class Card(Base):
    tablename = "cards"
    card_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    stripe_card_id = Column(String(50), unique=True)
    bin = Column(String(6))
    last4 = Column(String(4))
    exp_month = Column(Integer)
    exp_year = Column(Integer)
    status = Column(String(20), default="active")
    created_at = Column(TIMESTAMP, server_default=func.now())
