from config import get_session
from models.location import Location

class LocationService:
    def __init__(self):
        self.session = get_session()

    def _refresh(self):
        try:
            self.session.close()
        except:
            pass
        self.session = get_session()

    def get_all_locations(self, active_only=True):
        self._refresh()
        query = self.session.query(Location)
        if active_only:
            query = query.filter(Location.is_active == True)
        return query.order_by(Location.code).all()

    def add_location(self, code, aisle=None, rack=None,
                     bin=None, max_weight=None, max_volume=None):
        try:
            location = Location(
                code=code, aisle=aisle, rack=rack,
                bin=bin, max_weight=max_weight, max_volume=max_volume
            )
            self.session.add(location)
            self.session.commit()
            print(f"Lokasyon eklendi: {location}")
            return location
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Lokasyon eklenirken hata: {e}")

    def get_all_locations(self, active_only=True):
        query = self.session.query(Location)
        if active_only:
            query = query.filter(Location.is_active == True)
        return query.order_by(Location.code).all()

    def get_location_by_id(self, location_id):
        return self.session.get(Location, location_id)

    def get_location_by_code(self, code):
        return self.session.query(Location).filter_by(code=code).first()

    def deactivate_location(self, location_id):
        try:
            location = self.get_location_by_id(location_id)
            if not location:
                raise Exception("Lokasyon bulunamadı.")
            location.is_active = False
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Lokasyon pasife alınırken hata: {e}")