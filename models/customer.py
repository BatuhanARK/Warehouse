from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base

class Customer(Base):
    __tablename__ = "customers"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    code       = Column(String(20), nullable=False, unique=True)
    name       = Column(String(120), nullable=False)
    contact    = Column(String(80))
    email      = Column(String(100))
    phone      = Column(String(30))
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    stocks    = relationship("Stock",    back_populates="customer")
    movements = relationship("Movement", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.code} - {self.name}>"