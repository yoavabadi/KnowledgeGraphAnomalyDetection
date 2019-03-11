"""
    Wikidata Search Util Class
    Use: WikidataSearcher( [SEARCH_LIMIT [=DEFAULT_LIMIT]]).search( KEYWORD )
    :return nodes_dict and edges_list
    Performance for keyword 'DNA':
        timing for 10 results: 0.9274415969848633 sec.
        timing for 100 results: 0.9046275615692139 sec.
        timing for 1000 results: 1.082622766494751 sec.
        timing for 10000 results: 1.2751281261444092 sec.
"""
from SPARQLWrapper import SPARQLWrapper
import requests
import json
import re
from time import time, sleep
from WordFilter import WordFilter
QID_TOKEN = "Q_TOKEN"
DEFAULT_LIMIT = 10
QID_BASE_URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&limit=1&language=en&search="
SPARQL_URL = "https://query.wikidata.org/sparql"
QUERY_FORMAT = "SELECT DISTINCT ?item ?itemLabel WHERE {?item (wdt:P22*|wdt:P25*|wdt:P3373*|" \
               "wdt:P26*|wdt:P40*|wdt:P1038*|wdt:P106*|wdt:P101*|wdt:P39*|wdt:P551*|" \
               "wdt:P937*|wdt:P102*|wdt:P31*|wdt:P279*|wdt:P4330*) wd:" + QID_TOKEN + ". " \
               "SERVICE wikibase:label { bd:serviceParam wikibase:language 'en'. }}LIMIT "


class WikidataSearcher:
    """
    A class that query Wikidata
    """
    def __init__(self, limit=DEFAULT_LIMIT, common_words_limit=1000):
        self._limit = limit
        self.word_filter = WordFilter(common_words_limit, to_filter_relations=True)

    @staticmethod
    def _get_wikidata_qid(obj_name):
        """
        Getting the identity (the Q id) of the object
        :param obj_name: the name of the object we want to find its Q id
        :return: the name of the node and its Q id
        """
        link = QID_BASE_URL + obj_name
        r = requests.get(link, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        _qid = json.loads(r.text)['search'][0]['id']
        _name = json.loads(r.text)['search'][0]['label']
        return _qid, _name

    def search(self, obj_name):
        """
        Given a entity, find its page in wikidata, and do query about its properties:
·         P26- spouse
·         P40- child
·         P1038- relative
·         P106- occupation
·         P101- field of work
·         P39- position held
·         P551- residence
·         P937- work location
·         P102- member of political party
·         P31- instance of
·         P279- subclass of
·         P4330- contains
        and from its properties create more edges, including it and the property
        :param obj_name: the object we are querying wikidata with
        :return: the new edges and nodes
        """
        # t = time()
        obj_qid, obj_name = WikidataSearcher._get_wikidata_qid(obj_name)
        sparql = SPARQLWrapper(SPARQL_URL)
        query = QUERY_FORMAT.replace(QID_TOKEN, obj_qid) + str(self._limit)
        sparql.setQuery(query)
        sparql.setReturnFormat("json")
        results = sparql.query().convert()
        nodes_dict = {obj_qid: obj_name}
        edges_list = []
        for result in results["results"]["bindings"]:
            _id = result['item']['value'].split("/")[-1]
            _name = result['itemLabel']['value']
            if re.match(r"Q[0-9]+", _name) or _name == obj_name:
                continue
            temp, _name = WikidataSearcher._get_wikidata_qid(_id)
            if self.word_filter.filter_word(_name) and len(_name.split(" ")) <= 3 and _id != _name and \
                    not re.match(r"Q[0-9]+", _name) and not re.match(r"http://www.wikidata.org/entity/Q[0-9]+", _name):
                nodes_dict[_id] = _name
                edges_list.append((_id, obj_qid))
        return nodes_dict, edges_list
