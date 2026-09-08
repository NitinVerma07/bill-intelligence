import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String
from sqlalchemy.orm import relationship
from .database import Base


class BillTable(Base):
    __tablename__ = "bills"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_name = Column(String, nullable=True)
    subtotal = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    service_charge = Column(Float, default=0.0)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    other_tax = Column(Float, default=0.0)
    printed_total = Column(Float, default=0.0)
    calculated_total = Column(Float, default=0.0)
    image_path = Column(String, nullable=True)
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("BillItemTable", back_populates="bill", cascade="all, delete-orphan")


class BillItemTable(Base):
    __tablename__ = "bill_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bill_id = Column(String, ForeignKey("bills.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    source = Column(String, default="local_ocr")
    bbox = Column(JSON, nullable=True)
    needs_review = Column(Boolean, default=False)
    bill = relationship("BillTable", back_populates="items")
