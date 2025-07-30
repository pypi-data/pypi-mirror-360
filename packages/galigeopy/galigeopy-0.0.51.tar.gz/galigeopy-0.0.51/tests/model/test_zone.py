import unittest
import json

from galigeopy.org.org import Org
from galigeopy.model.zone import Zone
from galigeopy.model.poi import Poi

class TestZone(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])
        self.zone_type = self.org.getZoneTypeById(self.conf["zone_type_id"])

    def test_zone(self):
        zone = self.zone_type.getZoneById(self.conf["zone_id"])
        self.assertIsNotNone(zone)
        self.assertIsInstance(zone, Zone)
        self.assertEqual(zone.zone_id, self.conf["zone_id"])
        del zone

    def test_get_poi(self):
        zone = self.zone_type.getZoneById(self.conf["zone_id"])
        poi = zone.getPoi()
        self.assertIsNotNone(poi)
        self.assertIsInstance(poi, Poi)
        self.assertEqual(poi.poi_id, zone.poi_id)
        del zone

    def test_get_parent_zone(self):
        # TODO: Implement test
        pass

    def test_get_child_zones(self):
        # TODO: Implement test
        pass

    def test_get_zone_geounit_list(self):
        zone = self.zone_type.getZoneById(self.conf["zone_id"])
        df = zone.getZoneGeounitsList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertEqual(df.iloc[0]["zone_id"], self.conf["zone_id"])
        del zone

    def test_get_zone_geounit_by_id(self):
        zone = self.zone_type.getZoneById(self.conf["zone_id"])
        zone_geounit = zone.getZoneGeounitById(self.conf["zone_geounit_id"])
