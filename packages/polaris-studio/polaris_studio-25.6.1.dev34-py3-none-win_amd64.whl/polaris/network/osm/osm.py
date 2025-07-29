# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import bz2
import hashlib
import json
import logging
import os
import pickle
import warnings
from math import sqrt, ceil
from os.path import join, isfile
from tempfile import gettempdir
from time import sleep
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

from polaris.network.constants import OSM_NODE_RANGE
from polaris.network.starts_logging import logger
from polaris.network.tools.geo_index import GeoIndex
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.optional_deps import check_dependency
from .traffic_light import TrafficLight


class OSM:
    """Suite of geo-operations to retrieve data from Open-Street Maps

    **FOR LARGE MODELLING AREAS IT IS RECOMMENDED TO DEPLOY YOUR OWN OVERPASS SERVER**

    ::

        from os.path import join
        import sqlite3
        from datetime import timedelta
        from polaris.network.network import Network

        root = 'D:/Argonne/GTFS/CHICAGO'
        network_path = join(root, 'chicago2018-Supply.sqlite')

        net = Network()
        net.open(network_path)

        osm = net.osm

        # The first call to osm.get_traffic_signal() will download data for
        # the entire modelling area

        # Here we default to our own server
        osm.url = 'http://192.168.0.105:12345/api'
        # And we also set the wait time between queries to zero,
        # as we are not afraid of launching a DoS attack on ourselves
        osm.sleep_time = 0

        # If we want to list all nodes in the network that have traffic lights
        # We can get the distance to the closest traffic signal on OSM, including their OSM ID

        for node, wkb in net.conn.execute('Select node, ST_asBinary(geo) from Node').fetchall():
            geo = shapely.wkb.loads(wkb)
            tl = osm.get_traffic_signal(geo)
            print(f'{node}, {tl.distance}, {tl.osm_id}'

        # A more common use is within the Intersection/signal API
        # We would ALSO assign the url and sleep time EXACTLY as shown above
        for node in net.conn.execute('Select node from Node').fetchall():
            intersection = net.get_intersection(node)

            if intersection.osm_signal():
                intersection.delete_signal():
                sig = intersection.create_signal()
                sig.re_compute()
                sig.save()

        # We can also retrieve all hotels in the modelling area
        hotels = osm.get_tag('tourism', 'hotel')

        # Or all hospitals
        hosp = osm.get_tag('healthcare', 'hospital')

        # Universities
        universities = osm.get_tag('amenity', 'university')

        # or schools
        schools = osm.get_tag('amenity', 'school')


    """

    #: URL of the Overpass API
    # url_alt = "https://overpass.kumi.systems/api/interpreter"
    url = "https://overpass-api.de/api/interpreter"
    #: Pause between successive queries when assembling OSM dataset
    sleep_time = 1
    __tile_size = 500

    def __init__(self, path_to_file: os.PathLike) -> None:
        from polaris.utils.database.data_table_access import DataTableAccess
        from polaris.network.tools.geo import Geo

        polaris_logging()
        self.srid = get_srid(database_path=path_to_file)
        self.__data_tables = DataTableAccess(path_to_file)
        self.__geotool = Geo(path_to_file)

        self.__traffic_light_idx = GeoIndex()
        self.__traffic_lights = {}  # type: Dict[int, Any]

        self.links = {}  # type: Dict[int, Any]

        self.mode_link_idx: Dict[str, GeoIndex] = {}
        self._outside_zones = 0
        self.__osm_data: Dict[str, dict] = {}
        self.graphs: Dict[str, Any] = {}
        self.failed = True
        self._path_to_file = path_to_file

        self.__model_boundaries: Optional[Any] = None
        if self.srid > 0:
            self._set_srid(self.srid)

    def get_traffic_signal(self, point) -> TrafficLight:
        """Returns the traffic light object closest to the point provided

        Args:
            *point* (:obj:`Point`): A Shapely Point object

        Return:
            *traffic_light* (:obj:`TrafficLight`): Traffic light closest to the provided point
        """

        if not self.__traffic_light_idx.built:
            self.__build_traffic_light_index()

        nearest = list(self.__traffic_light_idx.nearest(point, 20))
        t = TrafficLight()
        if nearest:
            distances = [point.distance(self.__traffic_lights[x]) for x in nearest]
            t.distance = min(distances)
            t.osm_id = nearest[distances.index(t.distance)]
            t.geo = self.__traffic_lights[t.osm_id]

        return t

    def get_amenities(self, amenity_type: str) -> list:
        """Finds all [amenities] (<https://wiki.openstreetmap.org/wiki/Key:amenity>) with a certain type for the
            model area.

        Args:
            *amenity_type* (:obj:`str`): The value for the OSM tag 'amenity'

        Return:
            *amenities* (:obj:`list`): List of amenities in dictionary format.
        """
        queries = self.__tag_queries("amenity", amenity_type)

        self.__load_osm_data(tag="amenity", tag_value=amenity_type, queries=queries)
        return self.__osm_data["amenity"][amenity_type]

    def get_tag(self, tag: str, tag_value: str) -> list:
        """Finds all instances where a [given tag] (<https://wiki.openstreetmap.org/wiki/Key:amenity>)
            has a certain value at OSM.

        Args:
            *tag* (:obj:`str`): The tag of interest for download
            *tag_value* (:obj:`str`): The value for the OSM tag chosen

        Return:
            *amenities* (:obj:`list`): List of amenities in dictionary format.
        """
        queries = self.__tag_queries(tag, tag_value)
        self.__load_osm_data(tag=tag, tag_value=tag_value, queries=queries)
        return self.__osm_data[tag][tag_value]

    def __tag_queries(self, tag: str, tag_value: str) -> List[str]:
        return [
            f'[out:json][timeout:180];(node["{tag}"="{tag_value}"]["area"!~"yes"]' + "({});>;);out;",
            f'[out:json][timeout:180];(way["{tag}"="{tag_value}"]["area"!~"yes"]' + "({});>;);out;",
        ]

    def conflate_osm_walk_network(self, tolerance=10):  # pragma: no cover
        """It moves the link ends from the OSM_WALK on top of nodes from the
        roadway whenever they are closer than the tolerance, while also
        re-populating node_a and node_b fields with values known to be unique
        and mutually consistent.
        Each node from the roadway network can only have one node from the
        OSM_WALK network moved on top of them in order to prevent links from the
        OSM_WALK network to have their start and end at the same node.
        Args:
            *tolerance* (:obj:`Float`): Maximum distance to move a link end
        """
        check_dependency("shapely")
        import shapely.wkb

        self.__data_tables.refresh_cache()

        network = self.__data_tables.get("OSM_WALK")
        network.geo = network.geo.apply(shapely.wkb.loads)

        net_nodes = self.__data_tables.get("Node")
        net_nodes.geo = net_nodes.geo.apply(shapely.wkb.loads)

        sql = """select link_id,
                        st_asbinary(startpoint(geo)) from_node, startpoint(geo) from_geo,
                        X(startpoint(geo)) from_x, Y(startpoint(geo)) from_y ,
                        st_asbinary(endpoint(geo)) to_node, endpoint(geo) to_geo,
                         X(endpoint(geo)) to_x, Y(endpoint(geo)) to_y
                        from OSM_Walk"""

        with commit_and_close(self._path_to_file, spatial=True) as conn:
            df = pd.read_sql(sql, conn)

            sindex_status = conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0]
            if sindex_status is None:
                conn.execute("SELECT CreateSpatialIndex( 'OSM_Walk' , 'geo' );")
                conn.commit()
                if conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0] is None:
                    raise ValueError("OSM_Walk has no spatial index and we were not able to add one")
            elif sindex_status == 1:
                pass
            elif sindex_status == 0:
                conn.execute('select RecoverSpatialIndex("OSM_Walk", "geo");')
                if conn.execute("select CheckSpatialIndex('OSM_Walk', 'geo')").fetchone()[0] == 0:
                    raise ValueError("OSM_Walk has a broken spatial index and we were not able to recover it")
            elif sindex_status == -1:
                warnings.warn("There is something weird with the OSM_Walk spatial index. Better check it")

            network = network.merge(df, on="link_id")

            df = network.drop_duplicates(subset=["from_x", "from_y"])[["from_x", "from_y", "from_geo", "from_node"]]
            df.columns = ["x", "y", "orig_geo", "wkb"]
            df2 = network.drop_duplicates(subset=["to_x", "to_y"])[["to_x", "to_y", "to_geo", "to_node"]]
            df2.columns = ["x", "y", "orig_geo", "wkb"]
            osm_nodes = pd.concat([df, df2]).drop_duplicates(subset=["x", "y"])
            osm_nodes = osm_nodes.assign(node_id=np.arange(osm_nodes.shape[0]) + OSM_NODE_RANGE)

            # We update the OSM_Walk network with the newly computed OSM node IDs
            sql = f"""update OSM_Walk set node_a=? WHERE
                            StartPoint(geo)=? AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = buffer(?, {tolerance}))"""

            sql2 = f"""update OSM_Walk set node_b=? WHERE
                            EndPoint(geo)=? AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = buffer(?, {tolerance}))"""

            aux = osm_nodes[["node_id", "orig_geo", "orig_geo"]]
            aux.columns = ["a", "b", "c"]
            aux = aux.to_records(index=False).tolist()

            conn.executemany(sql, aux)
            conn.executemany(sql2, aux)
            conn.commit()

            # Update node_a
            osm_nodes.drop(columns=["orig_geo"], inplace=True)
            osm_nodes.columns = ["from_x", "from_y", "point_geo", "node_id"]

            osm_nodes.point_geo = osm_nodes.point_geo.apply(shapely.wkb.loads)
            network = network.merge(osm_nodes, how="left", on=["from_x", "from_y"])
            network.loc[:, "node_a"] = network.node_id
            network.drop(columns=["node_id", "point_geo"], inplace=True)

            # update node_b
            osm_nodes.columns = ["to_x", "to_y", "point_geo", "node_id"]
            network = network.merge(osm_nodes, how="left", on=["to_x", "to_y"])
            network.loc[:, "node_b"] = network.node_id
            network.drop(columns=["node_id", "point_geo"], inplace=True)

            # Build an index for the existing OSM nodes
            walk_node_idx = GeoIndex()
            walk_node_geos = {}
            for _, record in osm_nodes.iterrows():
                walk_node_idx.insert(feature_id=record.node_id, geometry=record.point_geo)
                walk_node_geos[record.node_id] = record.point_geo

            # Search for node correspondences
            association = {}
            for idx, rec in net_nodes.iterrows():
                nearest_list = list(walk_node_idx.nearest(rec.geo, 10))
                for near in nearest_list:
                    near_geo = walk_node_geos[near]
                    dist = near_geo.distance(rec.geo)
                    if dist > tolerance:
                        break

                    # Is that OSM node even closer to some other node?
                    if idx == self.__geotool.get_geo_item("node", near_geo):
                        association[near] = idx
                        break

            # update link geometries
            sql = """update OSM_Walk set geo = SetStartPoint(geo, GeomFromWKB(?,?)), node_a=? WHERE
                            StartPoint(geo)=GeomFromWKB(?,?) AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = GeomFromWKB(?,?))"""

            sql2 = """update OSM_Walk set geo = SetEndPoint(geo, GeomFromWKB(?,?)), node_b=? WHERE
                            EndPoint(geo)=GeomFromWKB(?,?) AND
                            ROWID IN (SELECT ROWID FROM SpatialIndex WHERE f_table_name = 'OSM_Walk'
                                      AND search_frame = GeomFromWKB(?,?))"""

            data_tot = []
            for near, node_from_net in association.items():
                old_geo = walk_node_geos[near]
                new_geo = net_nodes.geo.at[node_from_net]
                data_tot.append([new_geo.wkb, self.srid, node_from_net, old_geo.wkb, self.srid, old_geo.wkb, self.srid])

            conn.executemany(sql, data_tot)
            conn.executemany(sql2, data_tot)
            conn.commit()
            conn.execute('select RecoverSpatialIndex("OSM_Walk", "geo");')

    @property
    def model_boundaries(self):
        return self.__model_boundaries or self.__get_boundaries()

    def set_tile_size(self, tile_size: int):
        """The use of smaller values for *tile_size* is only recommended if queries are returning
        errors with the default value of 500.
        """
        self.__tile_size = tile_size

    def __load_osm_data(self, tag, tag_value, queries):
        """Loads data from OSM or cached to disk"""
        self.__ensure_data_structure(tag, tag_value)
        self.failed = False
        if self.__osm_data.get(tag, {}).get(tag_value, []):
            logging.info("Data already in memory")
            return
        cache_name = self.__cache_name(tag, tag_value)
        if isfile(cache_name):
            self.__osm_data[tag][tag_value] = self.__load_cache(cache_name)[tag][tag_value]
            logging.info("Data loaded from disk cache")
            return

        check_dependency("requests")
        import requests

        logging.info("Downloading OSM data")
        # We won't download any area bigger than 25km by 25km
        bboxes = self.__bounding_boxes()

        http_headers = requests.utils.default_headers()
        http_headers.update({"Accept-Language": "en", "format": "json"})
        sleept = 0
        for query in queries:
            for bbox in bboxes:
                sleep(sleept)
                bbox_str = ",".join([str(round(x, 6)) for x in bbox])
                data = {"data": query.format(bbox_str)}
                response = requests.post(self.url, data=data, timeout=180, headers=http_headers, verify=False)
                if response.status_code != 200:
                    self.__osm_data[tag][tag_value] = []
                    Warning("Could not download data")
                    logger.error(f"Could not download data for tag {tag}:{tag_value}")
                    self.failed = True
                    self.__osm_data[tag][tag_value] = []
                    return

                # get the response size and the domain, log result
                json_data = response.json()
                if "elements" in json_data:
                    self.__ingest_json(json_data, tag, tag_value)

                # Guarantees we don't sleep when we do a single query
                sleept = self.sleep_time

        with bz2.BZ2File(cache_name, "wb") as f:
            pickle.dump(self.__osm_data, f)
        logging.info(f"Finished loading OSM data for {tag}")

    def __ensure_data_structure(self, tag, tag_value):
        if tag not in self.__osm_data:
            self.__osm_data[tag] = {}
        self.__osm_data[tag][tag_value] = self.__osm_data[tag].get(tag_value, [])

    def __ingest_json(self, json_data, tag, tag_value):
        check_dependency("shapely")
        import shapely.wkb
        from shapely.geometry import Point

        elements = json_data["elements"]
        node_index = {x["id"]: [x["lon"], x["lat"]] for x in elements if x.get("type", {}) == "node"}
        for x in elements:
            if x.get("tags", {}).get(tag, "") != tag_value:
                continue
            if "lon" not in x and "nodes" in x:
                lon = lat = 0
                counter = 0
                # We get the geo-center of the points
                for nid in x["nodes"]:
                    if nid not in node_index:
                        continue
                    lon += node_index[nid][0]
                    lat += node_index[nid][1]
                    counter += 1
                point = Point(lon / counter, lat / counter)
            else:
                point = Point(x.get("lon", 0), x.get("lat", 0))
            point = shapely.ops.transform(self.__transformer.transform, point)
            if not self.__geotool.modeling_area.contains(point):
                continue
            x["lon"] = point.x
            x["lat"] = point.y
            self.__osm_data[tag][tag_value].append(x)

    def _json_from_file(self, json_path, tag, tag_value):
        self.__ensure_data_structure(tag, tag_value)
        with open(json_path, "rb") as f:
            json_data = json.load(f)
        self.__ingest_json(json_data, tag, tag_value)

    def __bounding_boxes(self):
        parts = ceil(sqrt(self.model_boundaries.area / (self.__tile_size * self.__tile_size * 1000 * 1000)))
        area_bounds = list(self.model_boundaries.bounds)
        area_bounds[1], area_bounds[0] = self.__reverse_transformer.transform(area_bounds[0], area_bounds[1])
        area_bounds[3], area_bounds[2] = self.__reverse_transformer.transform(area_bounds[2], area_bounds[3])
        if parts == 1:
            bboxes = [area_bounds]
        else:
            bboxes = []
            xmin, ymin, xmax, ymax = area_bounds
            ymin_global = ymin
            delta_x = (xmax - xmin) / parts
            delta_y = (ymax - ymin) / parts
            for _ in range(parts):
                xmax = xmin + delta_x
                for _ in range(parts):
                    ymax = ymin + delta_y
                    bboxes.append([xmin, ymin, xmax, ymax])
                    ymin = ymax
                xmin = xmax
                ymin = ymin_global
        return bboxes

    def __build_traffic_light_index(self):
        check_dependency("shapely")
        from shapely.geometry import Point

        # We build the spatial index with the traffic lights from OSM
        queries = ['[out:json][timeout:180];(node["highway"="traffic_signals"]["area"!~"yes"]({});>;);out;']
        if not self.__traffic_lights:
            self.__load_osm_data(tag="highway", tag_value="traffic_signals", queries=queries)

        self.__traffic_light_idx = GeoIndex()

        for element in self.__osm_data["highway"]["traffic_signals"]:
            tags = element.get("tags", {1: 1})
            hw = tags.get("highway", "")
            if hw == "traffic_signals":
                # Vectorizing this could prove helpful
                ts_geo = Point([element["lon"], element["lat"]])
                osm_id = element["id"]
                self.__traffic_lights[osm_id] = ts_geo
                self.__traffic_light_idx.insert(feature_id=osm_id, geometry=ts_geo)

    def __cache_name(self, element: str, tag_text: str):
        area_bounds = list(self.model_boundaries.bounds)

        m = hashlib.md5()
        m.update(element.encode())
        m.update(tag_text.encode())
        m.update("".join([str(x) for x in area_bounds]).encode())
        return join(gettempdir(), f"{m.hexdigest()}.pkl")

    def __load_cache(self, cache_name):
        logging.info(f"Loaded OSM data from disk cache - {cache_name}")
        with bz2.BZ2File(cache_name, "rb") as f:
            return pickle.load(f)

    def __get_boundaries(self):
        check_dependency("shapely")
        from shapely.geometry import Polygon, box

        self.__model_boundaries = Polygon(box(*self.__geotool.modeling_area.bounds))
        return self.__model_boundaries

    def _set_srid(self, srid: int) -> None:
        check_dependency("pyproj")
        from pyproj import Transformer

        self.srid = srid
        self.__transformer = Transformer.from_crs(4326, self.srid, always_xy=True)
        self.__reverse_transformer = Transformer.from_crs(self.srid, 4326, always_xy=True)
