import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, mapping
from shapely.geometry.base import BaseGeometry
import json
from sqlalchemy import text

from galigeopy.model.poi import Poi
from galigeopy.model.zone_geounit import ZoneGeounit

class Zone:
    # Constructor
    def __init__(
        self,
        zone_id:int,
        properties:dict,
        geolevel_id:int,
        zone_type_id:int,
        poi_id:int,
        parent_zone_id:int,
        geometry:BaseGeometry,
        org:'Org' # type: ignore
    ):
        # Infos
        self._zone_id = zone_id
        self._properties = properties
        self._geolevel_id = geolevel_id
        self._zone_type_id = zone_type_id
        self._poi_id = poi_id
        self._parent_zone_id = parent_zone_id
        self._geometry = geometry
        # Org
        self._org = org

    # Getters and setters
    @property
    def zone_id(self): return self._zone_id
    @property
    def properties(self): return self._properties
    @property
    def geolevel_id(self): return self._geolevel_id
    @property
    def zone_type_id(self): return self._zone_type_id
    @property
    def poi_id(self): return self._poi_id
    @property
    def parent_zone_id(self): return self._parent_zone_id
    @property
    def geometry(self): return self._geometry
    @property
    def org(self): return self._org

    # Public Methods
    def getPoi(self)->Poi:
        query = f"SELECT * FROM ggo_poi WHERE poi_id = {self.poi_id}"
        gdf = gpd.read_postgis(query, self._org.engine, geom_col='geom')
        if len(gdf) > 0:
            data = gdf.iloc[0].to_dict()
            data.update({"org": self._org})
            return Poi(**data)
        else:
            raise Warning(f"Poi {self.poi_id} not found in Zone {self.zone_id}")
        
    def getParentZone(self) -> 'Zone':
        query = f"SELECT * FROM ggo_zone WHERE zone_id = {self.parent_zone_id}"
        df = pd.read_sql(query, self._org.engine)
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self._org})
            return Zone(**data)
        else:
            raise Warning(f"Parent Zone {self.parent_zone_id} not found in Zone {self.zone_id}")
        
    def getChildrenZones(self)->list:
        query = f"SELECT * FROM ggo_zone WHERE parent_zone_id = {self.zone_id}"
        df = pd.read_sql(query, self._org.engine)
        zones = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self._org})
            zones.append(Zone(**data))
        return zones
    
    def getZoneGeounitsList(self) -> pd.DataFrame:
        query = f"SELECT * FROM ggo_zone_geounit WHERE zone_id = {self.zone_id}"
        return pd.read_sql(query, self._org.engine)
    
    def getZoneGeounitById(self, geounit_id:int) -> pd.DataFrame:
        query = f"SELECT * FROM ggo_zone_geounit WHERE zone_id = {self.zone_id} AND zone_geounit_id = {geounit_id}"
        df = pd.read_sql(query, self._org.engine)
        if len(df) > 0:
            data = df.iloc[0].to_dict()
            data.update({"org": self._org})
            return ZoneGeounit(**data)
        else:
            raise Warning(f"Geounit {geounit_id} not found in Zone {self.zone_id}")
        
    def getAllZoneGeounits(self) -> list:
        query = f"SELECT * FROM ggo_zone_geounit WHERE zone_id = {self.zone_id}"
        df = pd.read_sql(query, self._org.engine)
        zone_geounits = []
        for i in range(len(df)):
            data = df.iloc[i].to_dict()
            data.update({"org": self._org})
            zone_geounits.append(ZoneGeounit(**data))
        return zone_geounits
    
    def getGeolevel(self):
        return self._org.getGeolevelById(self.geolevel_id)
    
    def getGeoDataFrame(self)->gpd.GeoDataFrame:
        query = f"SELECT * FROM ggo_zone WHERE zone_id = {self.zone_id} AND geometry IS NOT NULL"
        gdf = gpd.read_postgis(query, self._org.engine, geom_col='geometry')
        if len(gdf) > 0:
            return gdf
        else:
            geolevel = self.getGeolevel()
            q = f"""
                SELECT
                    g.{geolevel.geounit_code} AS geounit_code,
                    z.properties AS zone_properties,
                    zg.properties AS zone_geounit_properties,
                    g.{geolevel.geom_field} AS geometry
                FROM ggo_zone z
                JOIN ggo_zone_geounit zg ON zg.zone_id = z.zone_id
                JOIN {geolevel.table_name} g ON g.{geolevel.geounit_code} = zg.geounit_code
                WHERE z.zone_id = {self.zone_id}
            """
            gdf = gpd.read_postgis(q, self._org.engine, geom_col=geolevel.geom_field)
            return gdf

    def add_to_model(self) -> int:
        if (self.zone_id is not None):
            # Update database
            geom_q = f"ST_GeomFromGeoJSON('{json.dumps(mapping(self.geometry))}')" if self.geometry is not None else 'NULL'
            query = f"""
            UPDATE ggo_zone SET
                properties = '{json.dumps(self.properties).replace("'", "''")}',
                geolevel_id = {self.geolevel_id if self.geolevel_id is not None else 'NULL'},
                zone_type_id = {self.zone_type_id},
                poi_id = {self.poi_id},
                parent_zone_id = {self.parent_zone_id if self.parent_zone_id is not None else 'NULL'},
                geometry = {geom_q}
            WHERE zone_id = {self.zone_id} RETURNING zone_id;
            """
            zone_id = self._org.query(query)[0][0]
            return zone_id
        # Add to database
        geom_q = f"ST_GeomFromGeoJSON('{json.dumps(mapping(self.geometry))}')" if self.geometry is not None else 'NULL'
        query = f"""
        INSERT INTO ggo_zone (
            properties,
            geolevel_id,
            zone_type_id,
            poi_id,
            parent_zone_id,
            geometry
        ) VALUES (
            '{json.dumps(self.properties).replace("'", "''")}',
            {self.geolevel_id if self.geolevel_id is not None else 'NULL'},
            {self.zone_type_id},
            {self.poi_id},
            {self.parent_zone_id if self.parent_zone_id is not None else 'NULL'},
            {geom_q}
        ) RETURNING zone_id;
        """
        zone_id = self._org.query(query)[0][0]
        return zone_id

    def plot(self, prop:str=None, plot_poi:bool=False)->'Axes':  # type: ignore
        # Get geolevel
        geolevel = self._org.getGeolevelById(self.geolevel_id)
        # Get list of geounits
        geounits = self.getZoneGeounitsList()
        geounits_code_list = geounits["geounit_code"].to_list()
        # Get geodata
        gdf = geolevel.getGeoDataset(geounits=geounits_code_list)
        # Plot
        if prop is not None:
            geounits["property_to_plot"] = geounits["properties"].apply(lambda x : x[prop])
            geounits = geounits[['geounit_code', 'property_to_plot']]
            gdf = gdf.merge(geounits, on="geounit_code")
            ax = gdf.plot(column='property_to_plot', legend=True)
            if plot_poi:
                poi = self.getPoi()
                x, y = poi.x, poi.y
                ax.scatter(x, y, color='red')
        else:
            ax = gdf.plot()
            if plot_poi:
                poi = self.getPoi()
                x, y = poi.x, poi.y
                ax.scatter(x, y, color='red')
        return ax