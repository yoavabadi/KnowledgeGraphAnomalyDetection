import networkx as nx
import numpy as np
from WordVector import WordVector
SIMS_FACTOR = 10
NUM_PATHS = 2
SIMILARITY = 1

####################################################################################################
# First algorithm as described in the paper:
####################################################################################################

##########################################################
# This is a LOop anomaly detection implementation from:  #
# https://github.com/vc1492a/PyNomaly                    #
# and the k-nn from:                                     #
# https://scikit-learn.org/stable/modules/neighbors.html #
from PyNomaly import loop
from sklearn.neighbors import NearestNeighbors


def get_anomalies_by_LOop(graph, k_nn, threshold):
    graph_matrix = nx.to_numpy_matrix(graph)
    neigh = NearestNeighbors(n_neighbors=k_nn, metric='hamming')
    neigh.fit(graph_matrix)
    d, idx = neigh.kneighbors(graph_matrix, return_distance=True)
    m = loop.LocalOutlierProbability(distance_matrix=d, neighbor_matrix=idx, n_neighbors=k_nn).fit()
    scores = m.local_outlier_probabilities
    nodes = []
    anomalies = []
    ragular = []
    for i, node in enumerate(graph.nodes):
        nodes.append(node)
        if scores[i] > threshold:
            anomalies.append(node)
        else:
            ragular.append(node)

    anomalies_edges = []
    for i in range(len(anomalies)):
        for j in range(len(anomalies)):
            if i != j and anomalies[j] in nx.all_neighbors(graph, anomalies[i]) \
                    and not (anomalies[j], anomalies[i]) in anomalies_edges:
                anomalies_edges.append((anomalies[i], anomalies[j]))
    return anomalies_edges


####################################################################################################
# Second algorithm as described in the paper:
####################################################################################################
def extract_features(graph):
    """
    Extracting features: the number of path with maximum length of 3, and the similarity between
    the two nodes in the edge.
    :param graph: the graph we extracting the features from
    :return: array of features, each cell contains the edge and uts features: number of paths and
    similarity
    """
    nodes = [node for node in graph.nodes]  # copy of nodes
    edges = [edge for edge in graph.edges]  # copy of edges
    word2vec = WordVector(nodes)
    model = word2vec.model
    word_vectors = model.wv
    edge_features = []
    # extract features
    for edge in edges:
        try:
            paths = len(list(nx.all_simple_paths(graph, source=edge[0], target=edge[1], cutoff=4)))
            node1 = edge[0]._name
            node2 = edge[1]._name
            if node1 == node2:
                continue
            if node1 in word_vectors.vocab and node2 in word_vectors.vocab:
                curr_similarity = model.similarity(w1=node1, w2=node2)
                edge_features.append(((node1, node2), curr_similarity, paths))
        except:
            continue
    return edge_features


def get_anomalies_by_center_of_mass(graph, pointer, amount=50):
    """
    Finding the anomalies, by finding the center of mass, and then the top #amount of distant points
    Since here we choose to classify a point as an anomaly by its distance, we have the parameter
    "amount", that indicates how many points we want to return. We can look at it as an array of
    points that each location indicates the distant from the center. From that reason, we will take
    each time a part of that list
    :param pointer: the pointer to the js files to inject to
    :param graph: the graph we need to find the anomaly to
    :param amount: the amount of edges we want to clasify as anomaly
    :return: the anomalies (the outliers)
    """
    features = extract_features(graph)
    sims_list = []
    lens_list = []
    for tup in features:
        sims_list.append(SIMS_FACTOR * tup[SIMILARITY])
        lens_list.append(tup[NUM_PATHS])
    sims_center = np.mean(np.asarray(sims_list))
    lens_center = np.mean(np.asarray(lens_list))
    outliers = []
    for tup in features:
        distance = np.sqrt((tup[1]-sims_center)**2 + (tup[2]-lens_center)**2)
        outliers.append((tup[0], distance))
    outliers = sorted(outliers, key=lambda x: x[1])
    res = str(pointer) + str(outliers[:amount])
    return res