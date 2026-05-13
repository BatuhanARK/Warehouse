from config import Base, engine

def create_tables():
    """Tüm tabloları veritabanında oluşturur."""
    from models import customer, product, location, stock, movement
    Base.metadata.create_all(engine)
    print("Tablolar başarıyla oluşturuldu.")