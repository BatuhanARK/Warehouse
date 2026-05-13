from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config import Base

class Movement(Base):
    __tablename__ = "movements"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    movement_type    = Column(String(10), nullable=False)   # IN / OUT / TRANSFER
    customer_id      = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id       = Column(Integer, ForeignKey("products.id"),  nullable=False)
    from_location_id = Column(Integer, ForeignKey("locations.id"))
    to_location_id   = Column(Integer, ForeignKey("locations.id"))
    quantity         = Column(Numeric(14, 3), nullable=False)
    reference        = Column(String(80))
    notes            = Column(Text)
    recorded_by      = Column(String(60))
    movement_date    = Column(Date, nullable=False)
    created_at       = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="movements")
    product  = relationship("Product",  back_populates="movements")
    from_loc = relationship("Location", back_populates="movements_from",
                            foreign_keys=[from_location_id])
    to_loc   = relationship("Location", back_populates="movements_to",
                            foreign_keys=[to_location_id])

    def __repr__(self):
        return f"<Movement {self.movement_type} qty={self.quantity} date={self.movement_date}>"