import requests
import asyncio
import aiohttp
import json
from pydantic import BaseModel
from typing import Optional, List

from .engine import Engine

class OsrmEngineParameters(BaseModel):
    url: str
    verified_url: bool
    default_profile: Optional[str] = "driving"
    default_version: Optional[str] = "v1"

class OsrmEngine(Engine):
    def __init__(self, parameters: dict, auto_test: bool = True):
        self._url = parameters.get('url')
        self._verified_url = parameters.get('verified_url')
        self._default_profile = parameters.get('default_profile', 'driving')
        self._default_version = parameters.get('default_version', 'v1')
        super().__init__("osrm", parameters, OsrmEngineParameters, auto_test=auto_test)

    @property
    def url(self): return self._url
    @property
    def verified_url(self): return self._verified_url
    @property
    def default_profile(self): return self._default_profile
    @property
    def default_version(self): return self._default_version

    def _check_status(self):
        """
        Check if the OSRM server is reachable.
        """
        try:
            response = requests.get(f"{self._url}route/v1/driving/13.388860,52.517037;13.397634,52.529407?overview=false", verify=self._verified_url)
            if response.status_code == 200:
                return True
            else:
                raise Exception(f"OSRM server is not reachable: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            raise Exception(f"Error connecting to OSRM server: {e}")
    
    def list_functions(self):
        return ["get_nearest", "get_route", "get_route_async", "get_table", "get_match", "get_trip", "get_tile"]
    
    def get_nearest(self, location:dict, number:int=1, version:str=None, profile:str=None)->list:
        """
        Get the nearest waypoints to a location.
        :param location: A dictionary with 'lat' and 'lng' keys.
        :param number: The number of nearest waypoints to return.
        :return: A list of waypoints.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/nearest/{v}/{p}/{location['lng']},{location['lat']}?number={number}"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        data = response.json()
        if data["code"] != "Ok":
            raise Exception(f"Error {data['code']}: {data['message']}")
        return data["waypoints"]
    
    def get_route(self, start, end, version:str=None, profile:str=None)->list:
        """
        Get the route between two locations.
        :param start: A dictionary with 'lat' and 'lng' keys for the start location.
        :param end: A dictionary with 'lat' and 'lng' keys for the end location.
        :return: A list of routes.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/route/{v}/{p}/{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == "Ok":
                return data["routes"]
            else:
                return []
        elif response.status_code == 400:
            data = response.json()
            if data["code"] == "NoRoute":
                return []
            else:
                raise Exception(f"Error {data['code']}: {data['message']}")
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
    def get_route_async(
        self,
        start:list,
        end:list,
        version:str=None,
        profile:str=None,
        alternatives:bool=False,
        steps:bool=False,
        annotations:bool=False,
        geometries:str="polyline",
        overview:str="simplified",
        continue_straight:str="default"
    )->list:
        """
        Get the route between multiple pairs of locations asynchronously.
        :param start: A list of dictionaries with 'lat' and 'lng' keys for the start locations.
        :param end: A list of dictionaries with 'lat' and 'lng' keys for the end locations.
        :return: A list of routes.
        """
        # Check start and end have the same length
        if len(start) != len(end):
            raise Exception("Start and end must have the same length")
        # Prepare urls
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        urls = []
        for i in range(len(start)):
            url = f"{self.url.removesuffix('/')}/route/{v}/{p}/{start[i]['lng']},{start[i]['lat']};{end[i]['lng']},{end[i]['lat']}"
            # Properties
            url += f"?alternatives={str(alternatives).lower()}"
            url += f"&steps={str(steps).lower()}"
            url += f"&annotations={str(annotations).lower()}"
            url += f"&geometries={geometries}"
            url += f"&overview={overview}"
            url += f"&continue_straight={continue_straight}"
            urls.append(url)
        # Async
        async def get(url, session):
            try:
                async with session.get(url=url) as response:
                    resp = await response.read()
                    return resp
            except Exception as e:
                pass
        async def main(urls):
            async with aiohttp.ClientSession() as session:
                ret = await asyncio.gather(*(get(url, session) for url in urls))
                return ret
        # Run
        data = asyncio.run(main(urls))
        # Check if noRoute
        json_data = [json.loads(d) for d in data]
        return [d for d in json_data]
    
    def get_table(self, locations:list, sources:list=None, destinations:list=None, version:str=None, profile:str=None)->list:
        """
        Get the distance and duration table between multiple locations.
        :param locations: A list of dictionaries with 'lat' and 'lng' keys for the locations.
        :param sources: A list of indices for the source locations.
        :param destinations: A list of indices for the destination locations.
        :return: A dictionary with the distance and duration table.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/table/{v}/{p}/"
        url += f";".join([f"{location['lng']},{location['lat']}" for location in locations])
        if sources or destinations:
            url += "?"
        if sources:
            url += f"sources={';'.join([str(source) for source in sources])}"
        if destinations:
            if sources:
                url += "&"
            url += f"destinations={';'.join([str(destination) for destination in destinations])}"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        data = response.json()
        if data["code"] != "Ok":
            raise Exception(f"Error {data['code']}: {data['message']}")
        del data["code"]
        return data
    
    def get_match(
        self,
        locations:list,
        steps:bool=False,
        geometries:str="polyline",
        annotations:bool=False,
        overview:str="simplified",
        timestamps:list=None,
        radiuses:list=None,
        version:str=None,
        profile:str=None
    )->list:
        """
        Match a GPS trace to the road network.
        :param locations: A list of dictionaries with 'lat' and 'lng' keys for the locations.
        :param steps: Whether to include steps in the response.
        :param geometries: The format of the geometries to return.
        :param annotations: Whether to include annotations in the response.
        :param overview: The level of detail for the overview geometry.
        :param timestamps: A list of timestamps for the locations.
        :param radiuses: A list of radiuses for the locations.
        :return: A list of matched routes.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/match/{v}/{p}/"
        url += f";".join([f"{location['lng']},{location['lat']}" for location in locations])
        # Properties
        url += f"?steps={str(steps).lower()}"
        url += f"&geometries={geometries}"
        url += f"&annotations={str(annotations).lower()}"
        url += f"&overview={overview}"
        if timestamps:
            url += f"&timestamps={';'.join([str(timestamp) for timestamp in timestamps])}"
        if radiuses:
            url += f"&radiuses={';'.join([str(radius) for radius in radiuses])}"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        data = response.json()
        if data["code"] != "Ok":
            raise Exception(f"Error {data['code']}: {data['message']}")
        del data["code"]
        return data
    
    def get_trip(
        self,
        locations:list,
        steps:bool=False,
        annotations:bool=False,
        geometries:str="polyline",
        overview:str="simplified",
        version:str=None,
        profile:str=None
    ):
        """
        Get a trip between multiple locations.
        :param locations: A list of dictionaries with 'lat' and 'lng' keys for the locations.
        :param steps: Whether to include steps in the response.
        :param annotations: Whether to include annotations in the response.
        :param geometries: The format of the geometries to return.
        :param overview: The level of detail for the overview geometry.
        :return: A dictionary with the trip information.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/trip/{v}/{p}/"
        url += f";".join([f"{location['lng']},{location['lat']}" for location in locations])
        # Properties
        url += f"?steps={str(steps).lower()}"
        url += f"&annotations={str(annotations).lower()}"
        url += f"&geometries={geometries}"
        url += f"&overview={overview}"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        data = response.json()
        if data["code"] != "Ok":
            raise Exception(f"Error {data['code']}: {data['message']}")
        del data["code"]
        return data
    
    def get_tile(
        self,
        x:int,
        y:int,
        zoom:int,
        version:str=None,
        profile:str=None
    )->bytes:
        """
        Get a tile from the OSRM server.
        :param x: The x coordinate of the tile.
        :param y: The y coordinate of the tile.
        :param zoom: The zoom level of the tile.
        :return: The tile data as bytes.
        """
        v = version if version else self.default_version
        p = profile if profile else self.default_profile
        url = f"{self.url.removesuffix('/')}/tile/{v}/{p}/tile({x},{y},{zoom}).mvt"
        response = requests.get(url, verify=self.verified_url)
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        return response.content