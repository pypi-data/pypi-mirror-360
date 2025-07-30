import unittest
import json
from sqlalchemy import Engine

from galigeopy.org.org import Org
from galigeopy.model.network import Network
from galigeopy.model.zone_type import ZoneType
from galigeopy.model.zone import Zone

class TestOrg(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))

    def test_org(self):
        # Valid Org
        org = Org(**self.conf["org"])
        self.assertTrue(org.is_valid)
        self.assertIsNotNone(org.engine)
        self.assertIsInstance(org.engine, Engine)
        del org
        # Invalid
        org = Org(user="xxx", password="xxx")
        self.assertFalse(org.is_valid)
        del org

    def test_query(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Query
        df = org.query("SELECT * FROM ggo_network")
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)

    def test_get_networks_list(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get networks list
        df = org.getNetworksList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        del org

    def test_get_network_by_id(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get network by id
        network = org.getNetworkById(self.conf["network_id"])
        self.assertIsNotNone(network)
        self.assertIsInstance(network, Network)
        self.assertEqual(network.network_id, self.conf["network_id"])
        del org

    def test_get_network_by_name(self):
        # Valid Org
        org = Org(**self.conf["org"])
        name = org.getNetworkById(self.conf["network_id"]).name
        # Get network by name
        network = org.getNetworkByName(name)
        self.assertIsNotNone(network)
        self.assertIsInstance(network, Network)
        self.assertEqual(network.name, name)
        self.assertEqual(network.network_id, self.conf["network_id"])
        del org

    def test_get_all_networks(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get all networks
        networks = org.getAllNetworks()
        self.assertIsNotNone(networks)
        self.assertGreater(len(networks), 0)
        self.assertIsInstance(networks[0], Network)
        del org

    def test_get_zone_types_list(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get zone types list
        df = org.getZoneTypesList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        del org

    def test_get_zone_type_by_id(self):
        # Valid Org
        org = Org(**self.conf["org"])
        zone_type = org.getZoneTypeById(self.conf["zone_type_id"])
        self.assertIsNotNone(zone_type)
        self.assertEqual(zone_type.zone_type_id, self.conf["zone_type_id"])
        del org

    def test_get_zone_type_by_name(self):
        # Valid Org
        org = Org(**self.conf["org"])
        name = org.getZoneTypeById(self.conf["zone_type_id"]).name
        # Get zone type by name
        zone_type = org.getZoneTypeByName(name)
        self.assertIsNotNone(zone_type)
        self.assertEqual(zone_type.name, name)
        self.assertEqual(zone_type.zone_type_id, self.conf["zone_type_id"])
        del org

    def test_get_all_zone_types(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get all zone types
        zone_types = org.getAllZoneTypes()
        self.assertIsNotNone(zone_types)
        self.assertGreater(len(zone_types), 0)
        self.assertIsInstance(zone_types[0], ZoneType)
        del org

    def test_get_geolevels_list(self):
        # Valid Org
        org = Org(**self.conf["org"])
        # Get geolevels list
        df = org.getGeolevelsList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        del org