import datetime
from os import error
import osmium

class OSMHandler(osmium.SimpleHandler):

    """
    [Class] OSMHandler
    This class stores the data form a .osm file
    to create  objects from this class from a file, do:
        osm_map = OSMHandler()
	    osm_map.apply_file(path)
    
    Properties:
        - nodes : [Node] array of nodes.
        - ways : [Way] array of ways.
        - relations : [Relations] array of relations
        - bounding_box : the bounding box of the OSM file

    Nested dictionary as 21/10/27
        - Node:
            changeset: (int)
            deleted: (boolean)
            id: (int)
            location:
                lat: (float)
                lon: (float)
                x: (int)
                y: (int)
            tags: List(key, value)
            timestamp: (datetime.datetime)
            uid: (int)
            user: (str)
            version: (int)
            visible: (boolean)
        - Way:
            nodes: []
                location:
                    x: (int)
                    y: (int)
                ref: (int)
                x: (int)
                y: (int)
            changeset: (int)
            deleted: (boolean)
            id: (int)
            tags: List(key, value)
            timestamp: (datetime.datetime)
            uid: (int)
            user: (str)
            version: (int)
            visible: (boolean)
    """

    def __init__(self):
        osmium.SimpleHandler.__init__(self)

        self.nodes = []
        self.ways  = []
        self.relations = []
        self.bounding_box = None

    def iter_to_list(self, iter):
        values = [self.get_value(i) for i in iter]
        return values

    def get_value(self, v):
        if not isinstance(v, (int, float, str, bool, datetime.datetime)):
            if hasattr(v, "__iter__"):
                return self.iter_to_list(v)
            else:
                return self.obj_to_dict(v)
        return v

    def obj_to_dict(self, obj):
        values = {}
        aux = [name for name in dir(obj) if not name.startswith('__')]
        for k in aux:
            try:
                v = getattr(obj, k)
            except: # enters here if cant find the attribute
                continue
            
            if callable(v):
                continue

            values[k] = self.get_value(v)
        return values

    def node(self, osm_node):
        self.nodes.append(self.obj_to_dict(osm_node))

    def way(self, osm_way):
        self.ways.append(self.obj_to_dict(osm_way))
    
    def relation(self, osm_relation):
        self.relations.append(self.obj_to_dict(osm_relation))

    def set_bounding_box(self,path):
        file = osmium.io.Reader(path, osmium.osm.osm_entity_bits.NOTHING)
        self.bounding_box = file.header().box()
