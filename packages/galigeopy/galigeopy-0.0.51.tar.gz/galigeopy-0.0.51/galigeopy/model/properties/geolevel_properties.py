from ..geolevel import Geolevel
import sqlparse

class GeolevelProperties:
    # Constructor
    def __init__(self, geolevel: Geolevel, geoleveldata_type_properties: list['GeoleveldataTypeProperties']): # type: ignore
        self._geolevel = geolevel
        self._geoleveldata_type_properties = geoleveldata_type_properties if geoleveldata_type_properties else []

    # Getters and setters
    @property
    def geolevel(self): return self._geolevel
    @property
    def geoleveldata_type_properties(self): return self._geoleveldata_type_properties
    @property
    def properties(self):
        geoleveldata_type_properties = []
        for gdtp in self._geoleveldata_type_properties:
            geoleveldata_type_properties += gdtp.properties
        return geoleveldata_type_properties
    
    def nb_properties(self):
        return len(self._geoleveldata_type_properties) + sum([gdtp.nb_properties() for gdtp in self._geoleveldata_type_properties])

    def sql_geoleveldata_type_properties(self):
        list_sql = []
        if len(self._geoleveldata_type_properties) == 0:
            return "gd.*"
        for prop in self._geoleveldata_type_properties:
            list_sql.append(f"{prop.to_sql(prefix='gd')}")
        return ", ".join(list_sql)
    
    def properties_sql(self):
        properties = []
        for gdtp in self._geoleveldata_type_properties:
            properties += gdtp.properties_sql()
        return properties
    
    def join_sql(self, source="zg.geounit_code"):
        join = []
        for gdtp in self._geoleveldata_type_properties:
            join += [f"JOIN ggo_geoleveldata AS gd ON gd.geounit_code = {source}"]
            join += gdtp.join_sql()
        return join
    
    def where_sql(self):
        where = [f"g.geolevel_id = {self._geolevel.geolevel_id}"]
        for gdtp in self._geoleveldata_type_properties:
            where += gdtp.where_sql()
        return where
    
    def to_sql(self, code=True, source="gd"):
        properties = [f"{source}.geounit_code AS geounit_code"] if code else []
        properties += self.properties_sql()
        q = f"""
        SELECT
            {', '.join(properties)}
        FROM ggo_geolevel AS g
        {' '.join(self.join_sql(source=source))}
        WHERE {" AND ".join(self.where_sql())}
        """
        return sqlparse.format(q, reindent=True, keyword_case='upper')