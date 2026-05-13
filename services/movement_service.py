from datetime import date
from config import get_session
from models.movement import Movement
from models.stock import Stock
from sqlalchemy.orm import joinedload
from decimal import Decimal


class InsufficientStockError(Exception):
    pass

class MovementService:
    def __init__(self):
        self.session = get_session()

    def _refresh(self):
        try:
            self.session.close()
        except:
            pass
        self.session = get_session()

    def get_movements(self, start_date=None, end_date=None,
                    customer_id=None, movement_type=None):
        self._refresh()
        query = self.session.query(Movement).options(
            joinedload(Movement.customer),
            joinedload(Movement.product),
            joinedload(Movement.from_loc),
            joinedload(Movement.to_loc),
        )
        if start_date:
            query = query.filter(Movement.movement_date >= start_date)
        if end_date:
            query = query.filter(Movement.movement_date <= end_date)
        if customer_id:
            query = query.filter(Movement.customer_id == customer_id)
        if movement_type:
            query = query.filter(Movement.movement_type == movement_type)
        return query.order_by(Movement.created_at.desc()).all()

    def _get_or_create_stock(self, customer_id, product_id, location_id):
        stock = self.session.query(Stock).filter_by(
            customer_id=customer_id,
            product_id=product_id,
            location_id=location_id
        ).first()
        if not stock:
            stock = Stock(
                customer_id=customer_id,
                product_id=product_id,
                location_id=location_id,
                quantity=0
            )
            self.session.add(stock)
        return stock

    def record_inbound(self, customer_id, product_id, to_location_id,
                    quantity, reference=None, notes=None):
        try:
            quantity = Decimal(str(quantity))   # ← ekle
            stock = self._get_or_create_stock(
                customer_id, product_id, to_location_id)
            stock.quantity += quantity
            movement = Movement(
                movement_type="IN",
                customer_id=customer_id,
                product_id=product_id,
                to_location_id=to_location_id,
                quantity=quantity,
                reference=reference,
                notes=notes,
                movement_date=date.today()
            )
            self.session.add(movement)
            self.session.commit()
            return movement
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Giriş kaydedilirken hata: {e}")

    def record_outbound(self, customer_id, product_id, from_location_id,
                        quantity, reference=None, notes=None):
        try:
            quantity = Decimal(str(quantity))   # ← ekle
            stock = self._get_or_create_stock(
                customer_id, product_id, from_location_id)
            if stock.quantity < quantity:
                raise InsufficientStockError(
                    f"Yetersiz stok! Mevcut: {stock.quantity}, İstenen: {quantity}"
                )
            stock.quantity -= quantity
            movement = Movement(
                movement_type="OUT",
                customer_id=customer_id,
                product_id=product_id,
                from_location_id=from_location_id,
                quantity=quantity,
                reference=reference,
                notes=notes,
                movement_date=date.today()
            )
            self.session.add(movement)
            self.session.commit()
            return movement
        except InsufficientStockError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Çıkış kaydedilirken hata: {e}")

    def record_transfer(self, customer_id, product_id,
                        from_location_id, to_location_id, quantity,
                        reference=None, notes=None):
        try:
            quantity = Decimal(str(quantity))   # ← ekle
            from_stock = self._get_or_create_stock(
                customer_id, product_id, from_location_id)
            if from_stock.quantity < quantity:
                raise InsufficientStockError(
                    f"Yetersiz stok! Mevcut: {from_stock.quantity}, İstenen: {quantity}"
                )
            from_stock.quantity -= quantity
            to_stock = self._get_or_create_stock(
                customer_id, product_id, to_location_id)
            to_stock.quantity += quantity
            movement = Movement(
                movement_type="TRANSFER",
                customer_id=customer_id,
                product_id=product_id,
                from_location_id=from_location_id,
                to_location_id=to_location_id,
                quantity=quantity,
                reference=reference,
                notes=notes,
                movement_date=date.today()
            )
            self.session.add(movement)
            self.session.commit()
            return movement
        except InsufficientStockError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Transfer kaydedilirken hata: {e}")

    def get_movements(self, start_date=None, end_date=None,
                      customer_id=None, movement_type=None):
        query = self.session.query(Movement)
        if start_date:
            query = query.filter(Movement.movement_date >= start_date)
        if end_date:
            query = query.filter(Movement.movement_date <= end_date)
        if customer_id:
            query = query.filter(Movement.customer_id == customer_id)
        if movement_type:
            query = query.filter(Movement.movement_type == movement_type)
        return query.order_by(Movement.created_at.desc()).all()