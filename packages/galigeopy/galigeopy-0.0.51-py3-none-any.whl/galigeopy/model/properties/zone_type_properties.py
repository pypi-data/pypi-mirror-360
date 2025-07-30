from .property import Property
from ..zone_type import ZoneType
import sqlparse

class ZoneTypeProperties:
    def __init__(
            self,
            zone_type: ZoneType,
            basic_zone_properties: list[Property],
            basic_zone_geounit_properties: list[Property],
            network_properties: list['NetworkProperties'] | None = None, # type: ignore
            geolevel_properties: list['GeolevelProperties'] | None = None, # type: ignore
        ):
        self._zone_type = zone_type
        self._basic_zone_properties = basic_zone_properties
        self._basic_zone_geounit_properties = basic_zone_geounit_properties
        self._network_properties = network_properties if network_properties else []
        self._geolevel_properties = geolevel_properties if geolevel_properties else []

    @property
    def zone_type(self): return self._zone_type
    @property
    def basic_zone_properties(self): return self._basic_zone_properties
    @property
    def basic_zone_geounit_properties(self): return self._basic_zone_geounit_properties
    @property
    def network_properties(self): return self._network_properties
    @property
    def geolevel_properties(self): return self._geolevel_properties
    @property
    def properties(self): 
        network_properties = [] 
        geolevel_properties = []
        for np in self._network_properties:
            network_properties += np.properties
        for gp in self._geolevel_properties:
            geolevel_properties += gp.properties
        return self._basic_zone_properties + self._basic_zone_geounit_properties + network_properties + geolevel_properties
    
    def nb_properties(self):
        return len(self._basic_zone_properties) + len(self._basic_zone_geounit_properties) + sum([np.nb_properties() for np in self._network_properties]) + sum([gp.nb_properties() for gp in self._geolevel_properties])

    def sql_basic_zone_properties(self):
        list_sql = []
        if len(self._basic_zone_properties) == 0:
            return "z.*"
        for prop in self._basic_zone_properties:
            list_sql.append(f"{prop.to_sql(prefix='z')}")
        return ", ".join(list_sql)

    def sql_basic_zone_geounit_properties(self):
        list_sql = []
        if len(self._basic_zone_geounit_properties) == 0:
            return "zg.*"
        for prop in self._basic_zone_geounit_properties:
            list_sql.append(f"{prop.to_sql(prefix='zg')}")
        return ", ".join(list_sql)
    
    def properties_sql(self):
        properties = []
        for prop in self._basic_zone_properties:
            properties.append(prop.to_sql(prefix="z"))
        for prop in self._basic_zone_geounit_properties:
            properties.append(prop.to_sql(prefix="zg"))
        for np in self._network_properties:
            properties += np.properties_sql()
        for gp in self._geolevel_properties:
            properties += gp.properties_sql()
        return properties
    
    def join_sql(self, label=False):
        join = ["JOIN ggo_zone_geounit AS zg ON zg.zone_id = z.zone_id"]
        join += ["JOIN ggo_poi AS p ON p.poi_id = z.poi_id"] if label else []
        for np in self._network_properties:
            join += ["JOIN ggo_poi AS p ON p.poi_id = z.poi_id"] if not label else []
            join += np.join_sql()
        for gp in self._geolevel_properties:
            join += ["JOIN ggo_geolevel AS g ON g.geolevel_id = z.geolevel_id"]
            join += gp.join_sql()
        return join

    def where_sql(self):
        where = [f"z.zone_type_id = {self._zone_type.zone_type_id}"]
        for np in self._network_properties:
            where += np.where_sql()
        for gp in self._geolevel_properties:
            where += gp.where_sql()
        return where
    
    def to_sql(self, z_idx=True, zg_idx=True, code=False, label=False):
        properties = [f"z.zone_id AS zone_id"] if z_idx else []
        properties += [f"zg.zone_geounit_id AS zone_geounit_id"] if zg_idx else []
        properties += [f"p.name AS poi_name"] if label else []
        properties += [f"zg.geounit_code AS geounit_code"] if code else []
        properties += self.properties_sql()
        q = f"""
        SELECT
            {', '.join(properties)}
        FROM ggo_zone AS z
        {' '.join(self.join_sql(label=label))}
        WHERE {" AND ".join(self.where_sql())}
        """
        return sqlparse.format(q, reindent=True, keyword_case='upper')