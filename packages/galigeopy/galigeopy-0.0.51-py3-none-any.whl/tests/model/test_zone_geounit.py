import unittest
import json

from galigeopy.org.org import Org
from galigeopy.model.zone_type import ZoneType
from galigeopy.model.zone import Zone
from galigeopy.model.poi import Poi
from galigeopy.model.zone_geounit import ZoneGeounit

class TestZoneType(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.conf = json.load(open("test-config.json"))
        self.org = Org(**self.conf["org"])
        self.zone_type = self.org.getZoneTypeById(self.conf["zone_type_id"])
        self.zone = self.zone_type.getZoneById(self.conf["zone_id"])
    
    def test_zone_geounit(self):
        zone_geounit = self.zone.getZoneGeounitById(self.conf["zone_geounit_id"])
        self.assertIsNotNone(zone_geounit)
        self.assertIsInstance(zone_geounit, ZoneGeounit)
        self.assertEqual(zone_geounit.zone_geounit_id, self.conf["zone_geounit_id"])
        del zone_geounit
    
    def test_get_zone_geounits_list(self):
        df = self.zone.getZoneGeounitsList()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertEqual(df.iloc[0]["zone_id"], self.conf["zone_id"])

    # def test_get_zone (self):
    #     zone = self.zone_geounit.getZone()
    #     self.assertIsNotNone(zone)
    #     self.assertIsInstance(zone, Zone)
    #     self.assertEqual(zone.zone_id, self.conf["zone_id"])
    #     del zone