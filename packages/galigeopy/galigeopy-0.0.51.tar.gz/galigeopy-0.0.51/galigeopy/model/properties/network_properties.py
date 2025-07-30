import sqlparse

from .property import Property
from .zone_type_properties import ZoneTypeProperties
from .distancier_properties import DistancierProperties
from ..network import Network

class NetworkProperties:
    def __init__(self, network: Network, basic_network_properties: list[Property], zone_type_properties: list[ZoneTypeProperties], distancier_properties: list[DistancierProperties]):
        self._network = network
        self._basic_network_properties = basic_network_properties
        self._zone_type_properties = zone_type_properties
        self._distancier_properties = distancier_properties

    @property
    def network(self): return self._network
    @property
    def basic_network_properties(self): return self._basic_network_properties
    @property
    def zone_type_properties(self): return self._zone_type_properties
    @property
    def distancier_properties(self): return self._distancier_properties
    @property
    def properties(self):
        zone_type_properties = []
        distancier_properties = []
        for zt in self._zone_type_properties:
            zone_type_properties += zt.properties
        for d in self._distancier_properties:
            distancier_properties += d.properties
        return self._basic_network_properties + zone_type_properties + distancier_properties
    
    def nb_properties(self):
        return len(self._basic_network_properties) + sum([zt.nb_properties() for zt in self._zone_type_properties]) + sum([d.nb_properties() for d in self._distancier_properties])
    
    def sql_basic_network_properties(self):
        list_sql = []
        if len (self._basic_network_properties) == 0:
            return "p.*"
        for prop in self._basic_network_properties:
            list_sql.append(f"{prop.to_sql(prefix='p')}")
        return list_sql
    
    def properties_sql(self):
        properties = []
        for prop in self._basic_network_properties:
            properties.append(prop.to_sql(prefix="p"))
        for zt in self._zone_type_properties:
            properties += zt.properties_sql()
        for d in self._distancier_properties:
            properties += d.properties_sql()
        return properties
    
    def join_sql(self):
        join = []
        for zt in self._zone_type_properties:
            join += ["JOIN ggo_zone AS z ON z.poi_id = p.poi_id", "JOIN ggo_zone_geounit AS zg ON zg.zone_id = z.zone_id"]
            join += zt.join_sql()
        for d in self._distancier_properties:
            j = 'poi_id_start' if d.distancier_session.network_id_start == self._network.network_id else 'poi_id_end'
            join += [f"JOIN ggo_distancier AS d ON d.{j} = p.poi_id", f"JOIN ggo_distancier_session AS ds ON ds.session_id = d.session_id"]
            join += d.join_sql()
        return join
    
    def where_sql(self):
        where = [f"p.network_id = {self._network.network_id}"]
        for zt in self._zone_type_properties:
            where += zt.where_sql()
        for d in self._distancier_properties:
            where += d.where_sql()
        return where
    
    def to_sql(self, idx=True, code=False, label=False):
        properties = ["p.poi_id AS poi_id"] if idx else []
        if code:
            properties.append("p.id AS poi_code")
        if label:
            properties.append("p.name AS poi_name")
        properties += self.properties_sql()
        group_by = idx + code + label + len(self._basic_network_properties)
        group_by = [str(i + 1) for i in range(group_by)]
        q = f"""
        SELECT
            {", ".join(properties)}
        FROM ggo_poi AS p
        {" ".join(self.join_sql())}
        WHERE {" AND ".join(self.where_sql())}
        GROUP BY {", ".join(group_by)}
        """
        return sqlparse.format(q, reindent=True, keyword_case='upper')
    