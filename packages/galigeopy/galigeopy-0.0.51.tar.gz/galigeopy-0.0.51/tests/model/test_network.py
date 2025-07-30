import unittest
import json

from galigeopy.org.org import Org
from galigeopy.model.poi import Poi

class TestNetwork(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])

    def test_network(self):
        network = self.org.getNetworkById(self.conf["network_id"])
        self.assertIsNotNone(network)
        self.assertEqual(network.org.engine, self.org.engine)

    def test_number_of_pois(self):
        network = self.org.getNetworkById(self.conf["network_id"])
        self.assertGreater(network.number_of_pois(), 0)

    def test_get_pois_list(self):
        network = self.org.getNetworkById(self.conf["network_id"])
        df = network.getPoisList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)

    def test_get_poi_by_code(self):
        network = self.org.getNetworkById(self.conf["network_id"])
        poi = network.getPoiByCode("0020500041")
        self.assertIsNotNone(poi)
        self.assertEqual(poi.id, "0020500041")
        self.assertIsNotNone(poi.x)
        self.assertIsNotNone(poi.y)
        self.assertEqual(poi.network_id, network.network_id)

    def test_get_all_pois(self):
        network = self.org.getNetworkById(self.conf["network_id"])
        pois = network.getAllPois()
        self.assertIsNotNone(pois)
        self.assertGreater(len(pois), 0)
        self.assertIsInstance(pois[0], Poi)
        self.assertEqual(pois[0].network_id, network.network_id)

