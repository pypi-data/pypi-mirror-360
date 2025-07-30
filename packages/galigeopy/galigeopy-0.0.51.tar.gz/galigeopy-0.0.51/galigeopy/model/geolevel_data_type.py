import pandas as pd
import geopandas as gpd
import json

from sqlalchemy import text
from galigeopy.model.properties.property import Property
from galigeopy.utils.types import pythonTypeToPostgresType

class GeolevelDataType:
    # Constructor
    def __init__(
            self,
            geoleveldata_type_id:int,
            name:str,
            properties:dict,
            geolevel_id:int,
            description:str,
            org:'Org' # type: ignore
    ):
        self._geoleveldata_type_id = geoleveldata_type_id
        self._name = name
        self._properties = properties
        self._geolevel_id = geolevel_id
        self._description = description
        self._org = org

    # Getters
    @property
    def geoleveldata_type_id(self): return self._geoleveldata_type_id
    @property
    def name(self): return self._name
    @property
    def properties(self): return self._properties
    @property
    def geolevel_id(self): return self._geolevel_id
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
    def getGeolevel(self):
        return self._org.getGeolevelById(self._geolevel_id)
    
    def getDataset(self)->pd.DataFrame:
        query = text(f"SELECT * FROM ggo_geoleveldata WHERE geoleveldata_type_id = {self._geoleveldata_type_id}")
        return pd.read_sql(query, self._org.engine)
    
    def getGeoDataset(self, columns=None)->gpd.GeoDataFrame:
        geolevel = self.getGeolevel()
        df_columns = pd.DataFrame(self._properties["columns"])
        if columns is not None:
            df_columns = df_columns[df_columns["colonne"].isin(columns)]
        p = []
        for index, row in df_columns.iterrows():
            p.append(f"(g.properties->>'{row['colonne']}')::{row['type']} AS {row['colonne']}")
        properties = ", ".join(p)
        properties = properties + "," if properties != "" else ""
        query = text(f"""
            SELECT
                g.geounit_code,
                {properties}
                geo.{geolevel.geom_field} AS geometry
            FROM ggo_geoleveldata g
            JOIN {geolevel.table_name} AS geo ON geo.{geolevel.geounit_code} = g.geounit_code
            WHERE
                geoleveldata_type_id = {self._geoleveldata_type_id}
        """)
        return gpd.read_postgis(query, self._org.engine, geom_col='geometry')
    
    def add_to_model(self) -> 'GeolevelDataType':
        # add to database
        query = f"""
            INSERT INTO ggo_geoleveldata_type (
                name,
                description,
                properties,
                geolevel_id
            ) VALUES (
                '{self._name.replace("'", "''")}',
                '{self._description.replace("'", "''")}',
                '{json.dumps(self._properties).replace("'", "''")}',
                {self._geolevel_id}
            ) RETURNING geoleveldata_type_id
        """
        geolevel_data_type_id = self._org.query(query)[0][0]
        self._geoleveldata_type_id = geolevel_data_type_id
        # return
        return self
    
    def update(self) -> 'GeolevelDataType':
        query = f"""
            UPDATE ggo_geoleveldata_type
            SET
                name = '{self._name.replace("'", "''")}',
                description = '{self._description.replace("'", "''")}',
                properties = '{json.dumps(self._properties).replace("'", "''")}',
                geolevel_id = {self._geolevel_id}
            WHERE geoleveldata_type_id = {self._geoleveldata_type_id}
        """
        self._org.query(query)
        return self
    
    def delete(self):
        query = f"DELETE FROM ggo_geoleveldata_type WHERE geoleveldata_type_id = {self._geoleveldata_type_id}"
        self._org.query(query)
        self._geoleveldata_type_id = None
        return True

    def getProperties(self, fast:int|None=None)->list[Property]:
        query = f"""
            SELECT
                gd.properties
            FROM ggo_geoleveldata AS gd
            WHERE gd.geoleveldata_type_id = {self._geoleveldata_type_id}
        """
        query += f" LIMIT {fast}" if fast is not None else ""
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

    
    @staticmethod
    def getAllGeolevelDataTypesOfGeolevel(geolevel):
        q = f"""
            SELECT
                DISTINCT gdt.*
            FROM ggo_geoleveldata_type AS gdt
            WHERE gdt.geolevel_id = {geolevel.geolevel_id}
        """
        org = geolevel.org
        df = geolevel.org.query_df(q)
        return [GeolevelDataType(**row, org=org) for row in df.to_dict(orient="records")]
