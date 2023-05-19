import copy

import redis
from redis.commands.graph import Node, Edge, Graph
from roger.roger_util import get_logger

logger = get_logger ()

"""Encode Python JSON-able objects as Cypher expressions."""


def encode_dict(obj):
    """Encode dictionary."""
    return "{" + ", ".join(
        f'`{key}`' + ": " + dumps(value)
        for key, value in obj.items()
    ) + "}"


def encode_list(obj):
    """Encode list."""
    return "[" + ", ".join(
        dumps(el) for el in obj
    ) + "]"


def encode_str(obj):
    """Encode string."""
    return f"\"{obj}\""


def encode_none(obj):
    """Encode None."""
    return "null"


def encode_bool(obj):
    """Encode boolean."""
    return "true" if obj else "false"


def dumps(obj):
    """Convert Python obj to Cypher expression."""
    if isinstance(obj, dict):
        return encode_dict(obj)
    elif isinstance(obj, list):
        return encode_list(obj)
    elif isinstance(obj, str):
        return encode_str(obj)
    elif isinstance(obj, bool):
        return encode_bool(obj)
    elif obj is None:
        return encode_none(obj)
    else:
        return str(obj)

class RedisGraph:
    """ Graph abstraction over RedisGraph. A thin wrapper but provides us some options. """
    
    def __init__(self, host='localhost', port=6379, graph='default', password=''):
        """ Construct a connection to Redis Graph. """
        self.r = redis.Redis(host=host, port=port, password=password)
        self.redis_graph = Graph(client=self.r,name=graph)
        self.edge_queries = []

    def add_node (self, identifier=None, label=None, properties=None):
        """ Add a node with the given label and properties. """
        # logger.debug (f"--adding node id:{identifier} label:{label} prop:{properties}")
        if identifier and properties:
            properties['id'] = identifier
        node = Node(node_id=identifier, label=label, properties=properties)
        self.redis_graph.add_node(node)
        return node

    def get_edge (self, start, end, predicate=None):
        """ Get an edge from the graph with the specified start and end identifiers. """
        result = None
        for edge in self.redis_graph.edges:
            if edge.src_node.id == start and edge.dest_node.id == end:
                result = edge
                break
        return result
    
    def add_edge (self, start, predicate, end, properties={}):
        """ Add an edge with the given predicate and properties between start and end nodes. """
        # logger.debug (f"--adding edge start:{start} pred:{predicate} end:{end} prop:{properties}")
        query = f"MATCH (a{{id: '{start}'}}), (b{{id: '{end}'}}) " \
                f"CREATE (a)-[e:{predicate}]->(b) SET e = {dumps(properties)}"

        self.edge_queries.append(query)

        return query

    # def add_edge_query(self, edges):
        # query = f"""
        # UNWIND {dumps(edges)} as e MATCH (a:`biolink:NamedThing`{{id: e.subject }}), (b:`biolink:NamedThing`{{id: e.object }}) CREATE (a)-[edge:e.predicate]->(b) SET edge = e
        # """
        # print(query)
        # self.query(query)


    def has_node (self, identifier):
        return identifier in self.redis_graph.nodes

    def get_node (self, identifier, properties=None):
        return self.redis_graph.nodes[identifier]
    
    def commit (self):
        """ Commit modifications to the graph. """
        self.redis_graph.commit()

    def query (self, query):
        """ Query and return result set. """
        result = self.redis_graph.query(query)
        # result.pretty_print()
        return result
    
    def delete (self):
        """ Delete the named graph. """
        self.redis_graph.delete()

    def flush(self):
        logger.debug (f"--STARTING FLUSH")
        self.redis_graph.flush()
        logger.debug (f"--FINISH FLUSH")
        for q in self.edge_queries:
            self.query(q)
        self.edge_queries = []
        logger.debug (f"--FINISH EDGE QUERIES")