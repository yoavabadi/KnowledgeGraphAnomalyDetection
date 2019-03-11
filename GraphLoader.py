"""
Loads The Nodes and Edges to form a Graph
"""
import re
import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import AnomalyDetection
import NERmodel
from WikidataSearcher import WikidataSearcher
from WordVector import WordVector
from sklearn.linear_model import RANSACRegressor
from sklearn.ensemble import IsolationForest

SIMS_FACTOR = 10

NUM_PATHS = 2
SIMILARITY = 1

# ~ Constants ~ #
DATA_FOLDER = "data/"
BASE_URL = "http://www.wikidata.org/entity/"
EDGES_FILE = os.path.join(DATA_FOLDER, "edges_file.txt")
EDGES_REGEX = r"(\(\'Q[0-9]+\'\,\s\'Q[0-9]+\'\))"


"""
Class representing a single node in the knowledge graph. The class holds the node's name and id. 
"""
class Node:
    def __init__(self, _id, _name):
        self._id = _id
        self._name = _name

    def __repr__(self):
        return self._name

    def __str__(self):
        return self._name



"""
Class holding the graph object. The nodes of the graph are object Node from the class above
"""
class GraphLoader:
    def __init__(self):
        self.graph = nx.Graph()

    @staticmethod
    def nodes_obj_dict(nodes_dict):
        """
        Creating dictionary of the given nodes by id
        :param nodes_dict: the dictionary of nodes
        :return: new dictionary, that the id is the key of the item Node
        """
        return {_id: Node(_id, _name) for _id, _name in nodes_dict.items()}

    @staticmethod
    def edges_obj_list(_nodes_obj_dict, edges_list):
        """
        Creating the edges according to a given edge list
        :param _nodes_obj_dict: the nodes to create edges from
        :param edges_list: the edge list
        :return: list of tuples: each tuple is an edge
        """
        return [(_nodes_obj_dict[edge[0]], _nodes_obj_dict[edge[1]])
                for edge in edges_list if edge[0] in _nodes_obj_dict and edge[1] in _nodes_obj_dict]

    def load_to_graph(self, _nodes_dict, _edges):
        """
        Laoding a graph accoring to the given edges and nodes
        :param _nodes_dict: the nodes
        :param _edges: the edges
        """
        _nodes = self.nodes_obj_dict(_nodes_dict)
        _edges = self.edges_obj_list(_nodes, _edges)
        for node in _nodes:
            self.graph.add_node(node)
        for edge in _edges:
            self.graph.add_edge(edge[0], edge[1])

    def remove_graph_nodes_by_degree(self, _degree):
        """
        Feature that represent a graph only with nodes wuth degree > _degree
        :param _degree: the minimum degree
        """
        # if self.graph.number_of_nodes()
        nodes_to_remove = ([node[0] for node in self.graph.degree if node[1] < _degree])
        self.graph.remove_nodes_from(nodes_to_remove)

    def remove_unconnected_graph_nodes(self):
        """
        Removing all nodes that has no connections
        :return:
        """
        self.remove_graph_nodes_by_degree(1)

    def draw_graph(self):
        """
        Drawing the graph
        """
        plt.axis('off')
        nx.draw(self.graph, with_labels=True, node_color='b')
        plt.show()

    def create_sub_graph(self, sub_nodes):
        """
        Represent a sub graph
        :param sub_nodes: the nodes to represent
        :return: the new graph to represent, with only the edges of the given nodes
        """
        return nx.Graph(self.graph.subgraph(sub_nodes))  # create a new graph


def load_keyword_temp_func():
    """
    Reading the entities file
    :return: the entities list
    """
    ENTITIES_REGEX = r"(\(\'[\w\s]+\'\,\s\'[\w\s]+\'\))"
    with open("data/entities_.txt", "r") as f:
        entities_edges = re.findall(ENTITIES_REGEX, f.read(), re.MULTILINE | re.DOTALL)
        entities_edges = [line[2:-2].replace(" '", "").replace("'", "").split(',') for line in
                          entities_edges]
        entities_nodes = list(set([item for sublist in entities_edges for item in sublist]))
        return entities_nodes, entities_edges


def graph_loader(text_files_arr, edges_limit=10, search_limit=10, common_words_limit=1000,
                 add_noun=False):
    """
    Creating a graph according to the given files
    :param text_files_arr: the fils to create graoh to
    :param edges_limit: the amount of edges to represent
    :param search_limit: How many new nodes to extract from a single entity
    :param common_words_limit: how many common words to filter
    :param add_noun: to add to the list of entities NOUN and not only PROPN
    """
    entities_edges = NERmodel.runner(text_files_arr, edges_limit, common_words_limit, add_noun)
    keywords = list(set([item for sublist in entities_edges for item in sublist]))
    nodes_dict, edges_list = {}, []

    # Example for possible use - search entities keywords from article,
    # to be combine and load to the graph
    graph_loader = GraphLoader()
    searcher = WikidataSearcher(limit=search_limit, common_words_limit=common_words_limit)
    for edge in entities_edges:
        try:
            values = nodes_dict.values()
            if edge[0] in values:
                _qid_1 = [i for i, j in nodes_dict.items() if j == edge[0]][0]
            else:
                _qid_1, _name_1 = searcher._get_wikidata_qid(edge[0])
                nodes_dict[_qid_1] = _name_1
            if edge[1] in values:
                _qid_2 = [i for i, j in nodes_dict.items() if j == edge[1]][0]
            else:
                _qid_2, _name_2 = searcher._get_wikidata_qid(edge[1])
                nodes_dict[_qid_2] = _name_2

            edges_list.append((_qid_1, _qid_2))
        except Exception as e:
            # prints all the edges we could not find any results in the query
            print(edge, e)

    for keyword in keywords:
        try:
            _nodes_dict, _edges_list = searcher.search(keyword.lower())
            nodes_dict = {**nodes_dict, **_nodes_dict}
            edges_list += _edges_list
        except Exception as e:
            continue
    graph_loader.load_to_graph(nodes_dict, edges_list)
    return graph_loader

