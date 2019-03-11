import AnomalyDetection
import GraphLoader
import webbrowser
import os

"""
Flow:
1. Build graph, using GraphLoader (who calls NERModel, for edges/relations)
2. Get the edges and the nodes
3. Detect anomalies.
4. Inject the nodes, edges, and anomalies to the js files through pointers
5. Load the newsGraph.html
"""

articles = ["data/articles/trump_2004", "data/articles/trump_2015", "data/articles/trump_2016",
            "data/articles/trump_2017", "data/articles/trump_2018"]
filename = 'WebGraph/newsGraph.html'

# 1
news_graph = GraphLoader.graph_loader(articles, edges_limit=1000,
                                      search_limit=10, common_words_limit=0, add_noun=False).graph

# The pointers we use in order to inject to the baseGraph.html file in order to create our newsGraph.html file
BASE_GRAPH_PATH = "WebGraph/baseGraph.html"
NODES_POINTER = "nodes: ["
EDGES_POINTER = "edges: ["
AUTOCOMPLETE_POINTER = "var autoCompleteOptions = {data: {}"
ANOMALY_POINTER = "var anomaliesEdges = []"
NODE_FORMAT = r"{data:{id:'{0}',name:'{1}'}},"
EDGE_FORMAT = r"{data:{source:'{0}',target:'{1}'}},"
nodes = NODES_POINTER
edges = EDGES_POINTER

# 2
nodes_names = [node._name for node in news_graph.nodes if type(node).__name__ != 'str'
         and news_graph.degree(node) > 0 and not node._name.startswith("Q")]
autocomplete_format = str({i: None for i in nodes_names}).replace("None", "null")
autocomplete = AUTOCOMPLETE_POINTER[:-2] + autocomplete_format + "\n"

for node in news_graph.nodes:
    if type(node).__name__ != 'str' and news_graph.degree(node) > 0 and not node._name.startswith("Q"):
        nodes += NODE_FORMAT.replace("{0}", node._id).replace("{1}", node._name)  # + "\n"

for edge in news_graph.edges:
    if edge[0]._id in nodes and edge[1]._id in nodes and edge[0]._id != edge[1]._id:
        edges += EDGE_FORMAT.replace("{0}", edge[0]._id).replace("{1}", edge[1]._id)  # + "\n"

# 3
anomalies = AnomalyDetection.get_anomalies_by_LOop(news_graph, k_nn=5, threshold=0.55)
anomalies = [[e[0]._id, e[1]._id] for e in anomalies]
anomalies = str(ANOMALY_POINTER)[:-2] + str(anomalies)

base_html = ""
with open(BASE_GRAPH_PATH, "r") as f:
    base_html += f.read()

# 4
html = base_html.replace(NODES_POINTER, nodes).replace(EDGES_POINTER, edges). \
    replace(AUTOCOMPLETE_POINTER, autocomplete).replace(ANOMALY_POINTER, anomalies)

with open(filename, "w+") as f:
    f.write(html)

# 5
webbrowser.open('file://' + os.path.realpath(filename))
