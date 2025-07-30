import pandas as pd
import geopandas as gpd
import json

from sqlalchemy import text

class Geolevel:
    # Constructor
    def __init__(
            self,
            geolevel_id:int,
            name:str,
            geounit_code:str,
            table_name:str,
            geom_field:str,
            geom_centroid_field:str,
            country:str,
            country_iso3:str,
            level:str,
            description:str,
            properties:str,
            sociodemo:dict,
            datahub_layer: str,
            org:'Org' # type: ignore
    ):
        # Infos
        self._geolevel_id = geolevel_id
        self._name = name
        self._geounit_code = geounit_code
        self._table_name = table_name
        self._geom_field = geom_field
        self._geom_centroid_field = geom_centroid_field
        self._country = country
        self._country_iso3 = country_iso3
        self._level = level
        self._description = description
        self._properties = properties
        self._sociodemo = sociodemo
        self._datahub_layer = datahub_layer
        # Engine
        self._org = org

    # Getters and setters
    @property
    def geolevel_id(self): return self._geolevel_id
    @property
    def name(self): return self._name
    @property
    def geounit_code(self): return self._geounit_code
    @property
    def table_name(self): return self._table_name
    @property
    def geom_field(self): return self._geom_field
    @property
    def geom_centroid_field(self): return self._geom_centroid_field
    @property
    def country(self): return self._country
    @property
    def country_iso3(self): return self._country_iso3
    @property
    def level(self): return self._level
    @property
    def description(self): return self._description
    @property
    def properties(self): return self._properties
    @property
    def sociodemo(self): return self._sociodemo
    @property
    def org(self): return self._org

    @name.setter
    def name(self, value): self._name = value
    @description.setter
    def description(self, value): self._description = value

    # Public Methods
    def getGeounitCodesList(self)->list:
        query = f"SELECT {self._geounit_code} FROM {self._table_name}"
        data = self._org.query(query)
        result = [row[0] for row in data]
        return result

    def getGeoDataset(self, all_data:bool=False, compute_centroid:bool=True, compute_centroid_crs:str="EPSG:2154", geounits:list=None)->gpd.GeoDataFrame:
        # Query
        query = f"SELECT * FROM {self._table_name}"
        if geounits is not None:
            str_geounits = ["'" + str(g) + "'" for g in geounits]
            query = f"{query} WHERE {self._geounit_code} IN ({', '.join([str(geounit) for geounit in str_geounits])})"
        # Get data from query
        gdf = gpd.read_postgis(query, self._org.engine, geom_col=self._geom_field)
        # Geounit_code column
        if self._geounit_code != "geounit_code":
            gdf["geounit_code"] = gdf[self._geounit_code]
            gdf = gdf.drop(columns=[self._geounit_code])
        gdf = gdf[["geounit_code"] + [col for col in gdf.columns if col != "geounit_code"]]
        # Centroid geometry
        if self._geom_centroid_field is None:
            if compute_centroid:
                gdf["geom_centroid"] = gdf[self._geom_field].to_crs(compute_centroid_crs).centroid.to_crs(gdf.crs)
            else:
                gdf["geom_centroid"] = None
        else:
            # Drop column
            gdf = gdf.drop(columns=[self._geom_centroid_field])
            query = f"SELECT {self._geounit_code}, {self._geom_centroid_field} FROM {self._table_name}"
            if geounits is not None:
                str_geounits = ["'" + str(g) + "'" for g in geounits]
                query = f"{query} WHERE {self._geounit_code} IN ({', '.join([geounit for geounit in str_geounits])})"
            # Get data from query
            gdf_centroid = gpd.read_postgis(query, self._org.engine, geom_col=self._geom_centroid_field)
            # Merge
            gdf = gdf.merge(gdf_centroid, left_on="geounit_code", right_on=self._geounit_code)
            # Rename column
            gdf = gdf.rename(columns={self._geom_centroid_field: "geom_centroid"})
        # Geometry in last
        if self._geom_field != "geom":
            gdf["geom"] = gdf[self._geom_field]
            gdf = gdf.drop(columns=[self._geom_field])
            gdf = gdf.set_geometry("geom")
        gdf = gdf[[col for col in gdf.columns if col != "geom"] + ["geom"]]
        # If not all data
        if not all_data:
            gdf = gdf[["geounit_code", "geom_centroid", "geom"]]
        # return df
        return gdf

    def getGeoCentroidDataset(self, geounits:list=None)->gpd.GeoDataFrame:
        # Query
        query = f"SELECT {self._geounit_code}, {self._geom_centroid_field} FROM {self._table_name}"
        if geounits is not None:
            str_geounits = ["'" + str(g) + "'" for g in geounits]
            query = f"{query} WHERE {self._geounit_code} IN ({', '.join([str(geounit) for geounit in str_geounits])})"
        # Get data from query
        gdf = gpd.read_postgis(query, self._org.engine, geom_col=self._geom_centroid_field)
        # Geounit_code column
        if self._geounit_code != "geounit_code":
            gdf["geounit_code"] = gdf[self._geounit_code]
            gdf = gdf.drop(columns=[self._geounit_code])
        gdf = gdf[["geounit_code"] + [col for col in gdf.columns if col != "geounit_code"]]
        # Geometry in last
        gdf = gdf.set_geometry(self._geom_centroid_field)
        # return df
        return gdf

    def getSocioDemoDataset(self, geounits:list=None)->pd.DataFrame:
        # Query
        query = self._sociodemo["query"]
        if geounits is not None:
            query = f"{query} WHERE {self._geounit_code} IN ({', '.join([str(geounit) for geounit in geounits])})"
        if query is not None:
            # Get data from query
            df = pd.read_sql(query, self._org.engine)
            # Geometry delete
            if "geometry" in df.columns:
                df = df.drop(columns=["geometry"], errors="ignore")
            else:
                raise Warning(f"No geometry column found in socio-demo query for geolevel {self._name}")
            # Geounit_code column in first
            if "geounit_code" in df.columns:
                df = df[["geounit_code"] + [col for col in df.columns if col != "geounit_code"]]
            else:
                raise Warning(f"No geounit_code column found in socio-demo query for geolevel {self._name}")
            # return df
            return df
        else:
            raise Warning(f"No socio-demo query found for geolevel {self._name}")
        
    def getGeoSocioDemoDataset(self, geounits:list=None)->gpd.GeoDataFrame:
        # Get geo dataset
        gdf = self.getGeoDataset(geounits=geounits)
        crs = gdf.crs
        gdf = gdf.drop(columns=["geom_centroid"])
        # Get socio demo dataset
        df = self.getSocioDemoDataset(geounits=geounits)
        # Merge
        gdf = pd.merge(df, gdf, on="geounit_code")
        # GeoDataFrame
        gdf = gpd.GeoDataFrame(gdf, geometry="geom", crs=crs)
        # return df
        return gdf
    
    def getJson(self)->dict:
        return {
            "geolevel_id": self._geolevel_id,
            "name": self._name,
            "geounit_code": self._geounit_code,
            "table_name": self._table_name,
            "geom_field": self._geom_field,
            "geom_centroid_field": self._geom_centroid_field,
            "country": self._country,
            "country_iso3": self._country_iso3,
            "level": self._level,
            "description": self._description,
            "properties": self._properties,
            "sociodemo": self._sociodemo
        }
    
    def add_to_model(self) -> int:
        # Add to database
        query = f"""
        INSERT INTO ggo_geolevel (
            name,
            geounit_code,
            table_name,
            geom_field,
            geom_centroid_field,
            country,
            country_iso3,
            level,
            description,
            properties,
            sociodemo
        )
        VALUES (
            '{self._name.replace("'", "''")}',
            '{self._geounit_code}',
            '{self._table_name}',
            '{self._geom_field}',
            {"'" + self._geom_centroid_field + "'" if self._geom_centroid_field is not None else 'NULL'},
            '{self._country.replace("'", "''")}',
            '{self._country_iso3}',
            '{self._level.replace("'", "''")}',
            '{self._description.replace("'", "''")}',
            '{json.dumps(self._properties).replace("'", "''")}',
            '{json.dumps(self._sociodemo).replace("'", "''")}'
        )
        RETURNING geolevel_id;
        """
        geolevel_id = self._org.query(query)[0][0]
        # Return
        return geolevel_id
    
    def number_of_geounits(self)->int:
        query = text(f"SELECT COUNT(*) FROM {self._table_name}")
        with self._org.engine.connect() as conn:
            result = conn.execute(query)
            return result.scalar()
        
    def update(self) -> 'Geolevel':
        query = f"""
        UPDATE ggo_geolevel
        SET
            name = '{self._name.replace("'", "''")}',
            geounit_code = '{self._geounit_code}',
            table_name = '{self._table_name}',
            geom_field = '{self._geom_field}',
            geom_centroid_field = {"'" + self._geom_centroid_field + "'" if self._geom_centroid_field is not None else 'NULL'},
            country = '{self._country.replace("'", "''")}',
            country_iso3 = '{self._country_iso3}',
            level = '{self._level.replace("'", "''")}',
            description = '{self._description.replace("'", "''")}',
            properties = '{json.dumps(self._properties).replace("'", "''")}',
            sociodemo = '{json.dumps(self._sociodemo).replace("'", "''")}'
        WHERE geolevel_id = {self._geolevel_id}
        """
        self._org.query(query)
        return self._org.getGeolevelById(self._geolevel_id)
    
    def delete(self)-> bool:
        query = f"DELETE FROM ggo_geolevel WHERE geolevel_id = {self._geolevel_id}"
        self._org.query(query)
        self._geolevel_id = None
        return True
    
    @staticmethod
    def getAllGeolevelOfZoneType(zone_type):
        q = f"""
        SELECT
            DISTINCT g.*
        FROM ggo_zone AS z
        JOIN ggo_geolevel AS g ON z.geolevel_id = g.geolevel_id
        WHERE z.zone_type_id = {zone_type.zone_type_id}
        """
        org = zone_type.org
        df = org.query_df(q)
        return [Geolevel(**row, org=org) for index, row in df.iterrows()]