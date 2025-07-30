import pandas as pd

class ClusterSession:
    def __init__(
        self,
        cluster_session_id:int | None,
        name:str,
        description:str,
        network_id:int | None,
        geolevel_id:int | None,
        properties:dict,
        org: 'Org' # type: ignore
    ):
        # Infos
        self._cluster_session_id = cluster_session_id
        self._name = name
        self._description = description
        self._network_id = network_id
        self._geolevel_id = geolevel_id
        self._properties = properties
        # Engine
        self._org = org

    def __str__(self):
        return self.name + " (" + str(self.cluster_session_id) + ")"
    
    # Getters
    @property
    def cluster_session_id(self): return self._cluster_session_id
    @property
    def name(self): return self._name
    @property
    def description(self): return self._description
    @property
    def network_id(self): return self._network_id
    @property
    def geolevel_id(self): return self._geolevel_id
    @property
    def properties(self): return self._properties
    @property
    def org(self): return self._org

    # Setters
    @name.setter
    def name(self, value): self._name = value
    @description.setter
    def description(self, value): self._description = value

    # Public Methods
    def number_of_clusters(self):
        query = f"SELECT COUNT(*) FROM ggo_cluster WHERE cluster_session_id = {self.cluster_session_id}"
        with self._org.engine.connect() as conn:
            result = conn.execute(query)
            return result.scalar()
        
    def getClustersList(self):
        query = f"SELECT * FROM ggo_cluster WHERE cluster_session_id = {self.cluster_session_id}"
        return pd.read_sql(query, self._org.engine)
    
    