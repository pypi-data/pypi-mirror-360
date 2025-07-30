# IMPORTS
from sqlalchemy import create_engine, Engine, text
import numpy as np
import pandas as pd
import geopandas as gpd

from galigeopy.model.network import Network
from galigeopy.model.poi import Poi
from galigeopy.model.zone_type import ZoneType
from galigeopy.model.geolevel import Geolevel
from galigeopy.model.geolevel_data_type import GeolevelDataType
from galigeopy.model.distancier_session import DistancierSession
from galigeopy.model.cluster_session import ClusterSession

class Org:
    # Constructor
    def __init__(self, user, password, host="127.0.0.1", port=5432, db="galigeo"):
        # Infos
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._db = db
        # Engine
        self._is_valid = False
        self._engine = self._get_engine()
        self._is_valid = self._check_validity()
        self._default_schema = self._get_default_schema()
    
    # Getters and setters
    @property
    def engine(self): return self._engine
    @property
    def is_valid(self): return self._is_valid
    @property
    def default_schema(self): return self._default_schema
    @property
    def name(self): return self._user.strip()

    # Private Methods
    def _get_engine(self) -> Engine:
        return create_engine(f'postgresql://{self._user}:{self._password}@{self._host}:{self._port}/{self._db}')

    def _get_default_schema(self)->str:
        query = "SELECT current_schema()"
        return self.query(query)[0][0]

    def _check_validity(self)->bool:
        # Check connection
        try:
            self._engine.connect()
            return True
        except Exception as e:
            return False
    
    # Public Methods
    def query_gdf(self, query:str, geometric_column:str="geometry", crs:str="EPSG:4326")->gpd.GeoDataFrame:
        gdf = gpd.read_postgis(query, self._engine, geom_col=geometric_column, crs=crs)
        return gdf

    def query_df(self, query:str, dtype:dict={})->pd.DataFrame:
        df = pd.read_sql_query(query, self._engine, dtype=dtype)
        return df

    def query(self, query:str)->list:
        with self._engine.connect() as conn:
            result = conn.execute(text(query))
            conn.commit()
            if result.returns_rows:
                return result.fetchall()
            else:
                return []

    def getNetworksList(self)->pd.DataFrame:
        # Query
        query = "SELECT * FROM ggo_network"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # return df
        return df
    
    def getNetworkById(self, id:int)->Network:
        # Query
        query = f"SELECT * FROM ggo_network WHERE network_id = {str(id)}"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return Network(**data)
        else:
            raise Warning(f"Network with id {id} not found")
    
    def getNetworkByName(self, name:str)->Network:
        # Query
        query = f"SELECT * FROM ggo_network WHERE name = '{name}'"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return Network(**data)
        else:
            raise Warning(f"Network with name {name} not found")
    
    def getAllNetworks(self)->list:
        # Query
        query = "SELECT * FROM ggo_network"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        networks = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            networks.append(Network(**data))
        return networks
    
    def getPoisByCode(self, code:str, networks_ids:list=[])->list:
        # Query
        query = f"SELECT * FROM ggo_poi WHERE id = '{code}'" if len(networks_ids) == 0 else f"SELECT * FROM ggo_poi WHERE id = '{code}' AND network_id IN ({','.join([str(i) for i in networks_ids])})"
        # Get data from query
        gdf = gpd.read_postgis(query, self._engine, geom_col="geom")
        # Data
        pois = []
        for i in range(len(gdf)):
            data = gdf.iloc[i].to_dict()
            data.update({"org": self})
            pois.append(Poi(**data))
        return pois
    
    def getZoneTypesList(self)->pd.DataFrame:
        # Query
        query = "SELECT * FROM ggo_zone_type"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # return df
        return df
    
    def getZoneTypeById(self, id:int)->ZoneType:
        # Query
        query = f"SELECT * FROM ggo_zone_type WHERE zone_type_id = {str(id)}"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return ZoneType(**data)
        else:
            raise Warning(f"ZoneType with id {id} not found")
        
    def getZoneTypeByName(self, name:str)->ZoneType:
        # Query
        name_sql = name.replace("'", "''")
        query = f"SELECT * FROM ggo_zone_type WHERE name = '{name_sql}'"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return ZoneType(**data)
        else:
            raise Warning(f"ZoneType with name {name} not found")
        
    def getAllZoneTypes(self)->list:
        # Query
        query = "SELECT * FROM ggo_zone_type"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        zone_types = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            zone_types.append(ZoneType(**data))
        return zone_types
    
    def getGeolevelsList(self)->pd.DataFrame:
        # Query
        query = "SELECT * FROM ggo_geolevel"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # return df
        return df
    
    def getGeolevelById(self, id:int)->Geolevel:
        # Query
        query = f"SELECT * FROM ggo_geolevel WHERE geolevel_id = {str(id)}"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return Geolevel(**data)
        else:
            raise Warning(f"Geolevel with id {id} not found")

    def getGeolevelByName(self, name:str)->Geolevel:
        # Query
        query = f"SELECT * FROM ggo_geolevel WHERE name = '{name}'"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return Geolevel(**data)
        else:
            raise Warning(f"Geolevel with name {name} not found")
        
    def getAllGeolevels(self)->list:
        # Query
        query = "SELECT * FROM ggo_geolevel"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        geolevels = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            geolevels.append(Geolevel(**data))
        return geolevels
    
    def getGeolevelDataTypesList(self)->pd.DataFrame:
        # Query
        query = "SELECT * FROM ggo_geoleveldata_type"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # return df
        return df
    
    def getGeolevelDataTypeById(self, id:int)->GeolevelDataType:
        # Query
        query = f"SELECT * FROM ggo_geoleveldata_type WHERE geoleveldata_type_id = {str(id)}"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return GeolevelDataType(**data)
        else:
            raise Warning(f"GeolevelDataType with id {id} not found")
        
    def getGeolevelDataTypeByName(self, name:str)->GeolevelDataType:
        # Query
        query = f"SELECT * FROM ggo_geoleveldata_type WHERE name = '{name}'"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self})
            return GeolevelDataType(**data)
        else:
            raise Warning(f"GeolevelDataType with name {name} not found")

    def getAllGeolevelDataTypes(self)->list:
        # Query
        query = "SELECT * FROM ggo_geoleveldata_type"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        geolevel_data_types = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            geolevel_data_types.append(GeolevelDataType(**data))
        return geolevel_data_types
        
    def getDistancierSessionList(self)->pd.DataFrame:
        # Query
        q = f"SELECT * FROM ggo_distancier_session"
        df = self.query_df(q)
        return df
    
    def getDistancierSessionById(self, session_id:int)->DistancierSession:
        # Query
        q = f"SELECT * FROM ggo_distancier_session WHERE session_id = {session_id}"
        df = self.query_df(q)
        if len(df) != 1:
            raise Warning(f"DistancierSession with id {session_id} doesn't exist")
        data = df.iloc[0].to_dict()
        data.update({"org": self})
        return DistancierSession(**data)
    
    def getDistancierSessionByName(self, name:str)->DistancierSession:
        # Query
        q = f"SELECT * FROM ggo_distancier_session WHERE name = '{name}'"
        df = self._org.query_df(q)
        if len(df) != 1:
            raise Warning(f"DistancierSession with name {name} doesn't exist")
        data = df.iloc[0].to_dict()
        data.update({"org": self})
        return DistancierSession(**data)
    
    def getAllDistancierSessions(self)->list:
        # query
        q = "SELECT * FROM ggo_distancier_session"
        df = self.query_df(q)
        # Data
        sessions = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            s = DistancierSession(**data)
            sessions.append(s)
        return sessions

    def getAllClusterSessions(self)->list:
        # Query
        query = "SELECT * FROM ggo_cluster_session"
        # Get data from query
        df = pd.read_sql(query, self._engine)
        # Data
        cluster_types = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self})
            cluster_types.append(ClusterSession(**data))
        return cluster_types


    
