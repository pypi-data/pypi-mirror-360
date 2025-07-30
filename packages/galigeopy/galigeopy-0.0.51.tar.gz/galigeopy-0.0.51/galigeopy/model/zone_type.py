import pandas as pd
import geopandas as gpd
from sqlalchemy import text
import json

from galigeopy.model.zone import Zone
from galigeopy.model.poi import Poi
from galigeopy.utils.types import pythonTypeToPostgresType
from galigeopy.model.properties.property import Property

class ZoneType:
    def __init__(
        self,
        zone_type_id:int,
        name:str,
        description:str,
        org: 'Org' # type: ignore
    ):
        # Infos
        self._zone_type_id = zone_type_id
        self._name = name
        self._description = description
        # Engine
        self._org = org

    def __str__(self):
        return self.name + " (" + str(self.zone_type_id) + ")"
    
    # Getters
    @property
    def zone_type_id(self): return self._zone_type_id
    @property
    def name(self): return self._name
    @property
    def description(self): return self._description
    @property
    def org(self): return self._org

    # Setters
    @name.setter
    def name(self, value): self._name = value
    @description.setter
    def description(self, value): self._description = value
    
    # Public Methods
    def number_of_zones(self):
        query = text(f"SELECT COUNT(*) FROM ggo_zone WHERE zone_type_id = {self.zone_type_id}")
        with self._org.engine.connect() as conn:
            result = conn.execute(query)
            return result.scalar()
        
    def getZonesList(self):
        query = text(f"SELECT * FROM ggo_zone WHERE zone_type_id = {self.zone_type_id}")
        df = self._org.query_df(query)
        # Properties to json
        df['properties'] = df['properties'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return df

    def getZoneById(self, zone_id:int):
        query = f"SELECT * FROM ggo_zone WHERE zone_id = {zone_id} AND zone_type_id = {self.zone_type_id}"
        df = self._org.query_df(query)
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self._org})
            return Zone(**data) 
        else:
            raise Warning(f"Zone {zone_id} not found in ZoneType {self.name}")
        
    def getZonesByPoi(self, poi : Poi):
        query = text(f"SELECT * FROM ggo_zone WHERE poi_id = {poi.poi_id} AND zone_type_id = {self.zone_type_id}")
        r = pd.read_sql(query, self._org.engine)
        zones = [Zone(**data, org=self._org) for data in r.to_dict(orient='records')]
        return zones
        
    def getAllZones(self):
        query = text(f"SELECT * FROM ggo_zone WHERE zone_type_id = {self.zone_type_id}")
        gdf = gpd.read_postgis(query, self._org.engine, geom_col='geometry')
        zones = []
        for i in range(len(gdf)):
            data = gdf.iloc[i].to_dict()
            data.update({"org": self._org})
            zones.append(Zone(**data))
        return zones
    
    def getAllPois(self) -> list:
        query = text(f"SELECT DISTINCT p.* FROM ggo_poi AS p JOIN ggo_zone AS z ON p.poi_id = z.poi_id WHERE z.zone_type_id = {self.zone_type_id} ORDER BY p.poi_id")
        gdf = gpd.read_postgis(query, self._org.engine, geom_col='geom')
        pois = [Poi(**data, org=self._org) for data in gdf.to_dict(orient='records')]
        # pois = list(set(pois))
        return pois
        
    def add_to_model(self)-> int:
        # Add to database
        query = f"""
        INSERT INTO ggo_zone_type (
            name,
            description
        ) VALUES (
            '{self.name.replace("'", "''")}',
            '{self.description.replace("'", "''")}'
        ) RETURNING zone_type_id;
        """
        zone_type_id = self._org.query(query)[0][0]
        return zone_type_id
    
    def update(self) -> 'ZoneType':
        query = f"""
        UPDATE ggo_zone_type
        SET
            name = '{self.name.replace("'", "''")}',
            description = '{self.description.replace("'", "''")}'
        WHERE zone_type_id = {self.zone_type_id}
        """
        self._org.query(query)
        return self._org.getZoneTypeById(self.zone_type_id)
    
    def delete(self)-> bool:
        query = f"DELETE FROM ggo_zone_type WHERE zone_type_id = {self.zone_type_id}"
        self._org.query(query)
        self._zone_type_id = None
        return True

    def getZonesProperties(self, fast:int|None=None)-> list[Property]:
        # Other properties
        query = f"""
        SELECT
            z.properties
        FROM ggo_zone AS z
        WHERE z.zone_type_id = {self.zone_type_id};
        """
        query += f" LIMIT {fast}" if fast else ""
        list_properties = self._org.query_df(query)['properties'].tolist()
        df_properties = pd.DataFrame(list_properties)
        df_prop = df_properties.dtypes.reset_index()
        df_prop.columns = ['columns', 'dtypes']
        df_prop['dtypes_postgres'] = df_prop['dtypes'].astype(str).apply(lambda x: pythonTypeToPostgresType(x))
        p = []
        for index, row in df_prop.iterrows():
            prop = Property(column='properties', dtype='JSONB', json_info={"key": row['columns'], "dtype": row['dtypes_postgres']})
            p.append(prop)
        return p
    
    def getZonesGeounitsProperties(self, fast:int|None=None)-> list[Property]:
        query = f"""
        SELECT
            zg.properties
        FROM ggo_zone_geounit AS zg
        JOIN ggo_zone AS z ON z.zone_id = zg.zone_id
        WHERE z.zone_type_id = {self.zone_type_id};
        """
        query += f" LIMIT {fast}" if fast else ""
        list_properties = self._org.query_df(query)['properties'].tolist()
        df_properties = pd.DataFrame(list_properties)
        df_prop = df_properties.dtypes.reset_index()
        df_prop.columns = ['columns', 'dtypes']
        df_prop['dtypes_postgres'] = df_prop['dtypes'].astype(str).apply(lambda x: pythonTypeToPostgresType(x))
        p = []
        for index, row in df_prop.iterrows():
            prop = Property(column='properties', dtype='JSONB', json_info={"key": row['columns'], "dtype": row['dtypes_postgres']})
            p.append(prop)
        return p
    
    def getProperties(self, fast:int|None=None)-> list[Property]:
        return self.getZonesProperties(fast=fast) + self.getZonesGeounitsProperties(fast=fast)
    
    @staticmethod
    def getAllZoneTypesOfNetwork(network):
        query = f"""
        SELECT
            DISTINCT zt.*
        FROM ggo_poi AS p
        JOIN ggo_zone AS z ON p.poi_id = z.poi_id
        JOIN ggo_zone_type AS zt ON z.zone_type_id = zt.zone_type_id
        WHERE p.network_id = {network.network_id}
        """
        org = network.org
        df = org.query_df(query)
        zone_types = [ZoneType(**data, org=org) for data in df.to_dict(orient='records')]
        return zone_types