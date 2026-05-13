"""
Test verisi oluşturma scripti.
Çalıştırmak için: python -m utils.seed_data
"""
from datetime import date, timedelta
import random
from decimal import Decimal
from models.base import create_tables
from config import get_session
from models.customer import Customer
from models.product import Product
from models.location import Location
from models.stock import Stock
from models.movement import Movement


def seed():
    create_tables()
    session = get_session()

    # ── Müşteriler ──────────────────────────────────────────
    musteriler = []
    musteri_data = [
        ("CUST-001", "ABC Lojistik"),
        ("CUST-002", "XYZ Depo"),
        ("CUST-003", "DEF Kargo"),
    ]
    for code, name in musteri_data:
        m = session.query(Customer).filter_by(code=code).first()
        if not m:
            m = Customer(code=code, name=name, phone="0212 000 0000")
            session.add(m)
            session.flush()
        musteriler.append(m)
    session.commit()
    print(f"✅ {len(musteriler)} müşteri hazır.")

    # ── Ürünler ─────────────────────────────────────────────
    urunler = []
    urun_data = [
        ("SKU-001", "Laptop",      "PCS", "Elektronik"),
        ("SKU-002", "Monitör",     "PCS", "Elektronik"),
        ("SKU-003", "Klavye",      "PCS", "Aksesuar"),
        ("SKU-004", "Mouse",       "PCS", "Aksesuar"),
        ("SKU-005", "Kulaklık",    "PCS", "Aksesuar"),
        ("SKU-006", "Tablet",      "PCS", "Elektronik"),
        ("SKU-007", "Kablo",       "KG",  "Sarf"),
        ("SKU-008", "Adaptör",     "PCS", "Sarf"),
    ]
    for sku, name, unit, cat in urun_data:
        p = session.query(Product).filter_by(sku=sku).first()
        if not p:
            p = Product(sku=sku, name=name, unit=unit, category=cat)
            session.add(p)
            session.flush()
        urunler.append(p)
    session.commit()
    print(f"✅ {len(urunler)} ürün hazır.")

    # ── Lokasyonlar ──────────────────────────────────────────
    lokasyonlar = []
    for aisle in ["A", "B", "C"]:
        for rack in ["01", "02", "03"]:
            for bin_ in ["01", "02"]:
                code = f"{aisle}-{rack}-{bin_}"
                loc  = session.query(Location).filter_by(code=code).first()
                if not loc:
                    loc = Location(
                        code=code, aisle=aisle,
                        rack=rack, bin=bin_
                    )
                    session.add(loc)
                    session.flush()
                lokasyonlar.append(loc)
    session.commit()
    print(f"✅ {len(lokasyonlar)} lokasyon hazır.")

    # ── Hareketler ───────────────────────────────────────────
    bugun        = date.today()
    # Önceki ay
    ay_basi      = date(bugun.year, bugun.month, 1)
    onceki_ay_son = ay_basi - timedelta(days=1)
    onceki_ay_bas = date(onceki_ay_son.year, onceki_ay_son.month, 1)
    # Sonraki ay
    if bugun.month == 12:
        sonraki_ay_bas = date(bugun.year + 1, 1, 1)
    else:
        sonraki_ay_bas = date(bugun.year, bugun.month + 1, 1)
    sonraki_ay_son = date(
        sonraki_ay_bas.year,
        sonraki_ay_bas.month + 1 if sonraki_ay_bas.month < 12 else 1,
        1
    ) - timedelta(days=1)

    # Tarih aralıkları
    tarih_araliklari = []

    # Önceki ay günleri
    gun = onceki_ay_bas
    while gun <= onceki_ay_son:
        tarih_araliklari.append(gun)
        gun += timedelta(days=1)

    # Bu ayın günleri (bugüne kadar)
    gun = ay_basi
    while gun <= bugun:
        tarih_araliklari.append(gun)
        gun += timedelta(days=1)

    # Sonraki ay günleri
    gun = sonraki_ay_bas
    while gun <= sonraki_ay_son:
        tarih_araliklari.append(gun)
        gun += timedelta(days=1)

    hareket_sayisi = 0
    random.seed(42)

    for tarih in tarih_araliklari:
        # Her gün 3-8 rastgele hareket
        for _ in range(random.randint(3, 8)):
            musteri  = random.choice(musteriler)
            urun     = random.choice(urunler)
            lokasyon = random.choice(lokasyonlar)
            miktar   = Decimal(str(random.randint(5, 100)))
            mv_type  = random.choice(["IN", "TRANSFER", "OUT"])  # IN ağırlıklı

            # Stok kontrolü
            stock = session.query(Stock).filter_by(
                customer_id=musteri.id,
                product_id=urun.id,
                location_id=lokasyon.id
            ).first()

            if mv_type == "OUT" or mv_type == "TRANSFER":
                if not stock or stock.quantity < miktar:
                    mv_type = "IN"

            if not stock:
                stock = Stock(
                    customer_id=musteri.id,
                    product_id=urun.id,
                    location_id=lokasyon.id,
                    quantity=Decimal("0")
                )
                session.add(stock)
                session.flush()

            if mv_type == "IN":
                stock.quantity += miktar
                from_loc = None
                to_loc   = lokasyon.id
            elif mv_type == "OUT":
                stock.quantity -= miktar
                from_loc = lokasyon.id
                to_loc   = None
            elif mv_type == "TRANSFER":
                # Farklı bir lokasyon seç
                diger_lokasyonlar = [l for l in lokasyonlar if l.id != lokasyon.id]
                hedef_lokasyon    = random.choice(diger_lokasyonlar)

                # Kaynak stoktan düş
                stock.quantity -= miktar

                # Hedef stoka ekle
                hedef_stock = session.query(Stock).filter_by(
                    customer_id=musteri.id,
                    product_id=urun.id,
                    location_id=hedef_lokasyon.id
                ).first()
                if not hedef_stock:
                    hedef_stock = Stock(
                        customer_id=musteri.id,
                        product_id=urun.id,
                        location_id=hedef_lokasyon.id,
                        quantity=Decimal("0")
                    )
                    session.add(hedef_stock)
                    session.flush()
                hedef_stock.quantity += miktar

                from_loc = lokasyon.id
                to_loc   = hedef_lokasyon.id

            movement = Movement(
                movement_type=mv_type,
                customer_id=musteri.id,
                product_id=urun.id,
                from_location_id=from_loc,
                to_location_id=to_loc,
                quantity=miktar,
                reference=f"REF-{tarih.strftime('%Y%m%d')}-{hareket_sayisi:04d}",
                movement_date=tarih
            )
            session.add(movement)
            hareket_sayisi += 1

        if hareket_sayisi % 100 == 0:
            session.commit()
            print(f"  → {hareket_sayisi} hareket eklendi...")

    session.commit()
    print(f"✅ Toplam {hareket_sayisi} hareket eklendi.")
    print(f"   Önceki ay: {onceki_ay_bas} - {onceki_ay_son}")
    print(f"   Bu ay:     {ay_basi} - {bugun}")
    print(f"   Sonraki ay: {sonraki_ay_bas} - {sonraki_ay_son}")
    session.close()


if __name__ == "__main__":
    seed()