import os

from gensim.test.utils import get_tmpfile
from gensim.models import Word2Vec
import re
import networkx as nx
import numpy as np
# from GraphLoader import load_keyword_temp_func
import gensim


def load_keyword_temp_func():
    """
    For dubugging purposes
    :return: edges and nodes of our graph
    """
    ENTITIES_REGEX = r"(\(\'[\w\s]+\'\,\s\'[\w\s]+\'\))"
    # regex_obj = re.compile(ENTITIES_REGEX, re.MULTILINE | re.DOTALL)
    with open("data/entities_.txt", "r") as f:
        entities_edges = re.findall(ENTITIES_REGEX, f.read(), re.MULTILINE | re.DOTALL)
        entities_edges = [line[2:-2].replace(" '", "").replace("'", "").split(',') for line in
                          entities_edges]
        entities_nodes = list(set([item for sublist in entities_edges for item in sublist]))
        return entities_nodes, entities_edges


class WordVector():
    """
    Model that receives the nodes
    """

    def __init__(self, nodes):
        self.model = self.create_model(nodes)

    def create_model(self, nodes):
        """
        Creates a model that given a set of words represents them as vector
        :param nodes: the nodes to learn
        :return: the model
        """
        new_nodes = []
        for value in nodes:
            tmp_list = [value._name]
            new_nodes.append(tmp_list)

        # min_count: threshold for frequency to ignore.
        # (for large DB, few appearances are probably typos)
        # size: number of NN layers
        # workes: something that rellevant for training speed, parallelization
        model = Word2Vec(new_nodes, size=200, window=5, min_count=1, workers=4)
        model.save('mymodel')
        new_model = Word2Vec.load('mymodel')
        index = gensim.similarities.MatrixSimilarity(gensim.matutils.Dense2Corpus(model.wv.syn0))
        counter = 0
        for sims in index:
            counter += 1
            # print(sims.shape)
        # print(counter)
        return new_model

    def get_model(self):
        return self.model
