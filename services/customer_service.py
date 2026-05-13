from config import get_session
from models.customer import Customer

class CustomerService:
    def __init__(self):
        self.session = get_session()

    def _refresh(self):
        try:
            self.session.close()
        except:
            pass
        self.session = get_session()

    def get_all_customers(self, active_only=True):
        self._refresh()
        query = self.session.query(Customer)
        if active_only:
            query = query.filter(Customer.is_active == True)
        return query.order_by(Customer.name).all()

    def add_customer(self, code, name, contact=None, email=None, phone=None):
        try:
            customer = Customer(
                code=code, name=name,
                contact=contact, email=email, phone=phone
            )
            self.session.add(customer)
            self.session.commit()
            print(f"Müşteri eklendi: {customer}")
            return customer
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Müşteri eklenirken hata: {e}")

    def get_all_customers(self, active_only=True):
        query = self.session.query(Customer)
        if active_only:
            query = query.filter(Customer.is_active == True)
        return query.order_by(Customer.name).all()

    def get_customer_by_id(self, customer_id):
        return self.session.get(Customer, customer_id)

    def get_customer_by_code(self, code):
        return self.session.query(Customer).filter_by(code=code).first()

    def update_customer(self, customer_id, **kwargs):
        try:
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                raise Exception("Müşteri bulunamadı.")
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            self.session.commit()
            return customer
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Müşteri güncellenirken hata: {e}")

    def deactivate_customer(self, customer_id):
        try:
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                raise Exception("Müşteri bulunamadı.")
            customer.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Müşteri pasife alınırken hata: {e}")