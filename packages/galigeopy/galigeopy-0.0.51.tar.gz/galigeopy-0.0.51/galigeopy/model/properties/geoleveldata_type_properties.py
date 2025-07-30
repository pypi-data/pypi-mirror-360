from ..geolevel_data_type import GeolevelDataType
from .property import Property

class GeoleveldataTypeProperties:
    def __init__(self, geoleveldata_type : GeolevelDataType, geoleveldata_properties: list[Property]):
        self._geoleveldata_type = geoleveldata_type
        self._geoleveldata_properties = geoleveldata_properties

    @property
    def geoleveldata_type(self): return self._geoleveldata_type
    @property
    def geoleveldata_properties(self): return self._geoleveldata_properties
    @property
    def properties(self): return self._geoleveldata_properties

    def nb_properties(self):
        return len(self._geoleveldata_properties)

    def sql_geoleveldata_properties(self):
        list_sql = []
        if len(self._geoleveldata_properties) == 0:
            return "gd.*"
        for prop in self._geoleveldata_properties:
            list_sql.append(f"{prop.to_sql(prefix='gd')}")
        return ", ".join(list_sql)
    
    def properties_sql(self):
        properties = []
        for prop in self._geoleveldata_properties:
            properties.append(prop.to_sql(prefix="gd"))
        return properties
    
    def join_sql(self):
        join = []
        return join
    
    def where_sql(self):
        where = [f"gd.geoleveldata_type_id = {self._geoleveldata_type.geoleveldata_type_id}"]
        return where
    
    def to_sql(self):
        return ""