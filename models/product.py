from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base

class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    sku         = Column(String(40), nullable=False, unique=True)
    name        = Column(String(150), nullable=False)
    description = Column(String(500))
    unit        = Column(String(20), default="PCS")
    weight_kg   = Column(Numeric(10, 3))
    category    = Column(String(60))
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())

    stocks    = relationship("Stock",    back_populates="product")
    movements = relationship("Movement", back_populates="product")

    def __repr__(self):
        return f"<Product {self.sku} - {self.name}>"