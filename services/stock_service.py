from config import get_session
from models.stock import Stock
from models.customer import Customer
from models.product import Product
from models.location import Location
from sqlalchemy import func
from sqlalchemy.orm import joinedload


class StockService:
    def __init__(self):
        self.session = get_session()

    def _refresh(self):
        try:
            self.session.close()
        except:
            pass
        self.session = get_session()

    def get_all_stock(self, customer_id=None, product_id=None, location_id=None):
        self._refresh()
        query = self.session.query(Stock).options(
            joinedload(Stock.customer),
            joinedload(Stock.product),
            joinedload(Stock.location),
        )
        if customer_id:
            query = query.filter(Stock.customer_id == customer_id)
        if product_id:
            query = query.filter(Stock.product_id == product_id)
        if location_id:
            query = query.filter(Stock.location_id == location_id)
        return query.all()

    def get_stock_by_id(self, stock_id):
        self._refresh()
        return self.session.query(Stock).options(
            joinedload(Stock.customer),
            joinedload(Stock.product),
            joinedload(Stock.location),
        ).filter(Stock.id == stock_id).first()

    def get_low_stock(self, threshold=10):
        self._refresh()
        return self.session.query(Stock).options(
            joinedload(Stock.customer),
            joinedload(Stock.product),
            joinedload(Stock.location),
        ).filter(
            Stock.quantity <= threshold,
            Stock.quantity > 0
        ).all()

    def get_total_by_product(self, product_id):
        self._refresh()
        result = self.session.query(
            func.sum(Stock.quantity)
        ).filter(Stock.product_id == product_id).scalar()
        return result or 0

    def get_stock_summary(self):
        self._refresh()
        return self.session.query(
            Customer.name.label("musteri"),
            Product.name.label("urun"),
            Product.sku.label("sku"),
            func.sum(Stock.quantity).label("toplam_miktar"),
            Product.unit.label("birim")
        ).join(Customer, Stock.customer_id == Customer.id
        ).join(Product, Stock.product_id == Product.id
        ).group_by(
            Stock.customer_id, Stock.product_id,
            Customer.name, Product.name, Product.sku, Product.unit
        ).all()