import unittest
import json
import pandas as pd
import geopandas as gpd

from galigeopy.org.org import Org
from galigeopy.model.geolevel import Geolevel

class TestGeolevel(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])

    def test_geolevel(self):
        geolevel = self.org.getGeolevelById(self.conf["geolevel_id"])
        self.assertIsNotNone(geolevel)
        self.assertIsInstance(geolevel, Geolevel)
        self.assertEqual(geolevel.geolevel_id, self.conf["geolevel_id"])
        del geolevel

    def test_get_geo_dataset(self):
        geolevel = self.org.getGeolevelById(self.conf["geolevel_id"])
        dataset = geolevel.getGeoDataset()
        self.assertIsNotNone(dataset)
        self.assertIsInstance(dataset, pd.DataFrame)
        self.assertGreater(len(dataset), 0)
        del geolevel, dataset

    def test_get_socio_demo_dataset(self):
        geolevel = self.org.getGeolevelById(self.conf["geolevel_id"])
        dataset = geolevel.getSocioDemoDataset()
        self.assertIsNotNone(dataset)
        self.assertIsInstance(dataset, pd.DataFrame)
        self.assertGreater(len(dataset), 0)
        del geolevel, dataset

    def test_get_geo_socio_demo_dataset(self):
        geolevel = self.org.getGeolevelById(self.conf["geolevel_id"])
        dataset = geolevel.getGeoSocioDemoDataset()
        self.assertIsNotNone(dataset)
        self.assertIsInstance(dataset, gpd.GeoDataFrame)
        self.assertGreater(len(dataset), 0)
        del geolevel, dataset

