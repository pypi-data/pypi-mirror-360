import unittest
import json

from galigeopy.org.org import Org
from galigeopy.model.zone_type import ZoneType

class TestZoneType(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])

    def test_zone_type(self):
        # Valid ZoneType
        zone_type = self.org.getZoneTypeById(self.conf["zone_type_id"])
        self.assertIsNotNone(zone_type)
        self.assertIsInstance(zone_type, ZoneType)
        self.assertEqual(zone_type.zone_type_id, self.conf["zone_type_id"])
        del zone_type

    def test_number_of_zones(self):
        # Valid ZoneType
        zone_type = self.org.getZoneTypeById(self.conf["zone_type_id"])
        number_of_zones = zone_type.number_of_zones()
        self.assertIsNotNone(number_of_zones)
        self.assertIsInstance(number_of_zones, int)
        self.assertGreater(number_of_zones, 0)
        del zone_type

    def test_get_zones_list(self):
        # Valid ZoneType
        zone_type = self.org.getZoneTypeById(self.conf["zone_type_id"])
        df = zone_type.getZonesList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertEqual(df.iloc[0]["zone_type_id"], self.conf["zone_type_id"])
        del zone_type