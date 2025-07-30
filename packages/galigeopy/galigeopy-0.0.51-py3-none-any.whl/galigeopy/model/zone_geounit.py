import pandas as pd
from sqlalchemy import text

class ZoneGeounit:
    # Constructor
    def __init__(
        self,
        zone_geounit_id:int,
        geounit_code:str,
        properties:dict,
        zone_id:int,
        org:'Org' # type: ignore
    ):
        # Infos
        self._zone_geounit_id = zone_geounit_id
        self._geounit_code = geounit_code
        self._properties = properties
        self._zone_id = zone_id
        # Engine
        self._org = org

    # Getters and setters
    @property
    def zone_geounit_id(self): return self._zone_geounit_id
    @property
    def geounit_code(self): return self._geounit_code
    @property
    def properties(self): return self._properties
    @property
    def zone_id(self): return self._zone_id
    @property
    def org(self): return self._org

    # Public Methods
    def getZone(self)->'Zone': # type: ignore
        query = text(f"SELECT zone_type_id FROM ggo_zone WHERE zone_id = {self.zone_id}")
        zone_type_id = self.org.query(query).iloc[0]["zone_type_id"]
        return self.org.getZoneTypeById(zone_type_id).getZoneById(self.zone_id)
    
