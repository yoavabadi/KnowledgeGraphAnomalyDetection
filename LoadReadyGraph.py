import re
import networkx as nx
from GraphLoader import Node
import AnomalyDetection

NUM_PATHS = 2
SIMILARITY = 1
GRAPH_PATH = 'WebGraph/newsGraph.html'


def get_graph():
    html = ""
    with open(GRAPH_PATH, "r") as f:
        html += f.read()

    nodes = (str(re.findall(r"\s*nodes:\s\[(.*)\],\n", html)).split(r"{data:{id:'")[1:-1])
    nodes = [node[:-len("'}},")] for node in nodes]
    nodes = [node.split("',name:'") for node in nodes]
    nodes_obj_dict = {n[0]: Node(n[0], n[1]) for n in nodes}

    edges = (str(re.findall(r"\s*edges:\s\[(.*)\]\n", html)).split(r"{data:{source:'")[1:])
    edges = [edge[:-len("'}},")] for edge in edges]
    edges = [edge.split("',target:'") for edge in edges]
    edges = [[nodes_obj_dict[n[0]], nodes_obj_dict[n[1]]] for n in edges if n[0] in nodes_obj_dict and n[1] in nodes_obj_dict]

    graph = nx.Graph()
    graph.add_nodes_from(nodes_obj_dict.values())
    graph.add_edges_from(edges)
    return graph


anomalies = AnomalyDetection.get_anomalies_by_LOop(get_graph(), k_nn=2, threshold=0.27)
print((anomalies))
