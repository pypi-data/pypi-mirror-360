import unittest
import json

from galigeopy.org.org import Org
from galigeopy.model.network import Network
from galigeopy.model.poi import Poi

class TestNetwork(unittest.TestCase):
    
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])
        self.network = self.org.getNetworkById(self.conf["network_id"])

    def test_poi(self):
        poi = self.network.getPoiByCode(self.conf["poi_code"])
        self.assertIsNotNone(poi)
        self.assertIsInstance(poi, Poi)
        self.assertEqual(poi.id, self.conf["poi_code"])
        self.assertIsNotNone(poi.x)