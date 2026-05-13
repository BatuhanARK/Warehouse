from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base

class Stock(Base):
    __tablename__ = "stock"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id  = Column(Integer, ForeignKey("products.id"),  nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    quantity    = Column(Numeric(14, 3), nullable=False, default=0)
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

    customer = relationship("Customer", back_populates="stocks")
    product  = relationship("Product",  back_populates="stocks")
    location = relationship("Location", back_populates="stocks")

    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", "location_id",
                         name="uq_stock_customer_product_location"),
    )

    def __repr__(self):
        return f"<Stock customer={self.customer_id} product={self.product_id} qty={self.quantity}>"
    