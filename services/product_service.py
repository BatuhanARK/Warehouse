from config import get_session
from models.product import Product

class ProductService:
    def __init__(self):
        self.session = get_session()

    def _refresh(self):
        try:
            self.session.close()
        except:
            pass
        self.session = get_session()

    def get_all_products(self, active_only=True):
        self._refresh()
        query = self.session.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.order_by(Product.name).all()

    def add_product(self, sku, name, unit="PCS", description=None,
                    weight_kg=None, category=None):
        try:
            product = Product(
                sku=sku, name=name, unit=unit,
                description=description,
                weight_kg=weight_kg, category=category
            )
            self.session.add(product)
            self.session.commit()
            print(f"Ürün eklendi: {product}")
            return product
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ürün eklenirken hata: {e}")

    def get_all_products(self, active_only=True):
        query = self.session.query(Product)
        if active_only:
            query = query.filter(Product.is_active == True)
        return query.order_by(Product.name).all()

    def get_product_by_id(self, product_id):
        return self.session.get(Product, product_id)

    def get_product_by_sku(self, sku):
        return self.session.query(Product).filter_by(sku=sku).first()

    def update_product(self, product_id, **kwargs):
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise Exception("Ürün bulunamadı.")
            for key, value in kwargs.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            self.session.commit()
            return product
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ürün güncellenirken hata: {e}")

    def deactivate_product(self, product_id):
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                raise Exception("Ürün bulunamadı.")
            product.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Ürün pasife alınırken hata: {e}")