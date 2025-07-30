import pandas as pd

class Poi:
    # Constructor
    def __init__(
            self,
            poi_id:int,
            id:str,
            address:str,
            postal_code:str,
            city:str,
            name:str,
            geounit_code:str,
            geocoder_accuracy:str,
            created_at:str,
            last_updated_at:str,
            last_updated_by:str,
            open_date:str,
            geom:str,
            properties:dict,
            network_id:int,
            logo_id:int,
            org:'Org' # type: ignore
    ):
        # Infos
        self._poi_id = poi_id
        self._id = id
        self._address = address
        self._postal_code = postal_code
        self._city = city
        self._name = name
        self._geounit_code = geounit_code
        self._geocoder_accuracy = geocoder_accuracy
        self._created_at = created_at
        self._last_updated_at = last_updated_at
        self._last_updated_by = last_updated_by
        self._open_date = open_date
        self._geom = geom
        self._properties = properties
        self._network_id = network_id
        self._logo_id = logo_id
        # Engine
        self._org = org

    # Getters and setters
    @property
    def poi_id(self): return self._poi_id
    @property
    def id(self): return self._id
    @property
    def address(self): return self._address
    @property
    def postal_code(self): return self._postal_code
    @property
    def city(self): return self._city
    @property
    def name(self): return self._name
    @property
    def geounit_code(self): return self._geounit_code
    @property
    def geocoder_accuracy(self): return self._geocoder_accuracy
    @property
    def created_at(self): return self._created_at
    @property
    def last_updated_at(self): return self._last_updated_at
    @property
    def last_updated_by(self): return self._last_updated_by
    @property
    def open_date(self): return self._open_date
    @property
    def geom(self): return self._geom
    @property
    def x(self): return float(self._geom.x)
    @property
    def y(self): return float(self._geom.y)
    @property
    def properties(self): return self._properties
    @property
    def network_id(self): return self._network_id
    @property
    def logo_id(self): return self._logo_id
    @property
    def org(self): return self._org

    # Magic Methods
    def __str__(self):
        return self.name + " (" + self.id + ")"
    
