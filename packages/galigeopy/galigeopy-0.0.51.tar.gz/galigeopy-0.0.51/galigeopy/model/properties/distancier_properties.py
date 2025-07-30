from .property import Property
from ..distancier_session import DistancierSession
import sqlparse

class DistancierProperties:
    def __init__(
            self,
            distancier_session: DistancierSession,
            basic_distancier_properties: list[Property],
            geolevel_properties: list['GeolevelProperties'] | None = None, # type: ignore
            network_properties: list['NetworkProperties'] | None = None # type: ignore
            ):
        self._distancier_session = distancier_session
        self._distancier_properties = basic_distancier_properties
        self._geolevel_properties = geolevel_properties if geolevel_properties else []
        self._network_properties = network_properties if network_properties else []

    @property
    def distancier_session(self): return self._distancier_session
    @property
    def distancier_properties(self): return self._distancier_properties
    @property
    def geolevel_properties(self): return self._geolevel_properties
    @property
    def network_properties(self): return self._network_properties
    @property
    def properties(self):
        network_properties = []
        geolevel_properties = []
        for np in self._network_properties:
            network_properties += np.properties
        for gp in self._geolevel_properties:
            geolevel_properties += gp.properties
        return self._distancier_properties + network_properties + geolevel_properties
    
    def nb_properties(self):
        return len(self._distancier_properties) + sum([np.nb_properties() for np in self._network_properties]) + sum([gp.nb_properties() for gp in self._geolevel_properties])

    def sql_distancier_properties(self):
        list_sql = []
        if len(self._distancier_properties) == 0:
            return "d.*"
        for prop in self._distancier_properties:
            list_sql.append(f"{prop.to_sql(prefix='d')}")
        return ", ".join(list_sql)
    
    def properties_sql(self):
        properties = []
        for prop in self._distancier_properties:
            properties.append(prop.to_sql(prefix="d"))
        for np in self._network_properties:
            properties += np.properties_sql()
        for gp in self._geolevel_properties:
            properties += gp.properties_sql()
        return properties
    
    def join_sql(self, code=False):
        join = []
        if code:
            j = 'poi_id_start' if self._distancier_session.network_id_start else 'poi_id_end'
            join += [f"JOIN ggo_poi AS p ON p.poi_id = d.{j}"] if code else []
        for np in self._network_properties:
            j = 'poi_id_start' if np.network.network_id == self._distancier_session.network_id_start else 'poi_id_end'
            join += [f"JOIN ggo_poi AS p ON p.poi_id = d.{j}"] if code else []
            join += np.join_sql()
        for gp in self._geolevel_properties:
            j = 'geolevel_id_start' if gp.geolevel.geolevel_id == self._distancier_session.geolevel_id_start else 'geolevel_id_end'
            join += [f"JOIN ggo_geolevel AS g ON g.geolevel_id = ds.{j}"]
            join += gp.join_sql(source="d.geounit_code_end")
        return join
    
    def where_sql(self):
        where = [f"d.session_id = {self._distancier_session.session_id}"]
        for np in self._network_properties:
            where += np.where_sql()
        for gp in self._geolevel_properties:
            where += gp.where_sql()
        return where
    
    def to_sql(self, idx=True, code=False):
        properties = []
        if idx:
            properties += ["d.poi_id_start::INTEGER AS poi_id_start"] if self.distancier_session.network_id_start else []
            properties += ["d.geounit_code_start::TEXT AS geounit_code_start"] if self.distancier_session.geolevel_id_start else []
            properties += ["d.poi_id_end::INTEGER poi_id_end"] if self.distancier_session.network_id_end else []
            properties += ["d.geounit_code_end::TEXT AS geounit_code_end"] if self.distancier_session.geolevel_id_end else []
        if code:
            properties += ["p.id::TEXT AS poi_code_start"] if self.distancier_session.network_id_start else []
            properties += ["d.geounit_code_start::TEXT AS geounit_code_start"] if self.distancier_session.geolevel_id_start else []
            properties += ["p.id ::TEXT AS poi_code_end"] if self.distancier_session.network_id_end else []
            properties += ["d.geounit_code_end::TEXT AS geounit_code_end"] if self.distancier_session.geolevel_id_end else []
        properties += self.properties_sql()
        q = f"""
        SELECT
            {', '.join(properties)}
        FROM ggo_distancier AS d
        JOIN ggo_distancier_session AS ds ON ds.session_id = d.session_id
        {' '.join(self.join_sql(code=code))}
        WHERE {" AND ".join(self.where_sql())}
        """
        return sqlparse.format(q, reindent=True, keyword_case='upper')
