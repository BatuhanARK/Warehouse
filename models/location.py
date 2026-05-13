from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy.orm import relationship
from config import Base

class Location(Base):
    __tablename__ = "locations"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    code       = Column(String(30), nullable=False, unique=True)
    aisle      = Column(String(10))
    rack       = Column(String(10))
    bin        = Column(String(10))
    max_weight = Column(Numeric(10, 2))
    max_volume = Column(Numeric(10, 3))
    is_active  = Column(Boolean, default=True)

    stocks            = relationship("Stock",    back_populates="location")
    movements_from    = relationship("Movement", back_populates="from_loc",
                                    foreign_keys="Movement.from_location_id")
    movements_to      = relationship("Movement", back_populates="to_loc",
                                    foreign_keys="Movement.to_location_id")

    def __repr__(self):
        return f"<Location {self.code}>"