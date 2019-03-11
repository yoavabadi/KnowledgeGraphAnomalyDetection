import spacy
# import spacy.cli
# spacy.cli.download("en_core_web_md")
from WordFilter import WordFilter
from nltk.stem import PorterStemmer

ps = PorterStemmer()

###################################################################################################
MAX_WORDS = 3

def exatrctor_pos_based_prop(analyzed_page, common_words_limit, add_noun):
    """
    Creates sequences of PROPN in order to extract the entities
    :param analyzed_page: the article we learning
    :param common_words_limit: the amount of common word to filter- if a words is in the top of
    common_words_limit, we will filter the entity
    :return: the entities we extracted
    """
    # find sequnces of PROPN
    in_seq = []
    prop_list = []
    limit = 0 if not add_noun else common_words_limit
    word_filter = WordFilter(limit, to_filter_relations=False)
    for i, word in enumerate(analyzed_page):
        if word_filter.filter_word(word.text):
            if (word.pos_ != 'PROPN' or (add_noun and word.pos_ != 'NOUN')) and len(in_seq) != 0:
                prop_list.append(in_seq)
                in_seq = []
            else:
                # filter nodes with more then MAX_WORDS
                if word.pos_ == 'PROPN' or (add_noun and word.pos_ == 'NOUN'):
                    # filter nodes with more then MAX_WORDS
                    in_seq.append(word)
        elif len(in_seq) != 0:
                prop_list.append(in_seq)
                in_seq = []

    return prop_list


def is_not_punct_and_verb(sub_page):
    """
    Receives a sub sentence between two entities, and return true if no punctuation is between them,
    and that there is a verb describing the relations between them
    :param sub_page: the sub sentence
    :return: True if there are no punctuation between them, and that there is a verb describing
    the relations between them
    """
    verb_in_sen = False
    for word in sub_page:
        if word.pos_ == 'PUNCT':
            return False
        if word.pos_ == 'VERB':
            verb_in_sen = True
    return verb_in_sen


def build_wordss_histogram(words):
    """
    How many from each word there is
    :param words: the words to count
    :return:
    """
    histogram = {}
    for noun in words:
        noun_as_string = repr(noun)  # lists cant be dictionary keys in python
        if noun_as_string in histogram:
            histogram[noun_as_string] += 1
        else:
            histogram[noun_as_string] = 1
    return histogram


def extractor_of_entities(analyzed_page, common_words_limit, add_noun):
    """
    From everry two adjacent words, we will understand if there is a relaion between them according
    to is_not_punct_and_verb, and if so we will add this pairs of entities to the list
    :param analyzed_page: the article we learning
    :param common_words_limit: the amount of common word to filter- if a words is in the top of
    common_words_limit, we will filter the entity
    :return: the pairs of entities
    """
    proper_nouns = exatrctor_pos_based_prop(analyzed_page, common_words_limit, add_noun)
    npunct_pairs = []
    for first_np, edge1 in enumerate(proper_nouns):
        if first_np + 1 < len(proper_nouns):
            second_np = first_np + 1
            edge2 = proper_nouns[second_np]
            sub_page = analyzed_page[edge1[-1].i + 1:edge2[0].i]
            if is_not_punct_and_verb(sub_page):
                sen1 = [(c.text) for c in edge1]
                sen2 = [(c.text) for c in edge2]
                npunct_pairs.append((" ".join(sen1), " ".join(sen2)))
    pairs = []
    for s1, s2 in npunct_pairs:  # remove duplicates
        if (s1, s2) not in pairs and (s2, s1) not in pairs:
            pairs.append((s1, s2))
    return pairs


def extractor_of_entities_with_relation(analyzed_page, common_words_limit, add_noun):
    """
    From everry two adjacent words, we will understand if there is a relaion between them according
    to is_not_punct_and_verb, and if so we will add this pairs of entities to the list
    :param analyzed_page: the article we learning
    :param common_words_limit: the amount of common word to filter- if a words is in the top of
    common_words_limit, we will filter the entity
    :return: the pairs of entities, with the relation between them
    """
    pairs = extractor_of_entities(analyzed_page, common_words_limit, add_noun)
    triples = []
    for np1, np2 in pairs:
        relation = []
        sub_page = analyzed_page[np1[-1].i + 1:np2[0].i]
        for word in sub_page:
            if word.pos_ == 'VERB' or word.pos_ == 'ADP':
                relation.append(word.text)
        if relation:
            sen1 = [ps.stem(c.text) for c in np1]
            sen2 = [ps.stem(c.text) for c in np2]
            triples.append((" ".join(sen1), relation, " ".join(sen2)))
    return triples


#####################################################################################################

def analyze_result(edges, article, edges_limit):
    """
    Prints the results according to the limit: we will print and save from edges only edges_limit
    from them
    :param edges: the list of relations we found
    :param article: the name of the file we extracting relations from
    :param edges_limit: the limit of edges we will save
    :return:
    """
    #   print(triples)
    print("For article " + article + " there are- " + str(len(edges)))
    print('\n')
    # if len(edges) > edges_limit:
    #     edges = edges[:edges_limit]
    for i in edges:
        print(i)
    print('\n')
    return edges


def runner(article_path, edges_limit, common_words_limit, add_noun):
    """
    The runner creates relations entities between any two entities find in a given array of article.
    The assumption is that the articles are part of the same domain and in general the same subject.
    At the end, we will write all the result we have found to a file
    :param article_path: the array of pathes to the articles
    :param edges_limit: the number od edges\relations we want to return
    :param common_words_limit: from the list of common words, how many of them we wish to filter
    from the entities in order to receive the main entities
    """
    nlp_model = spacy.load('en_core_web_md')
    articles = article_path
    total = 0
    edges = []
    for art in articles:
        with open(art, "r", encoding='utf-8') as f:
            page = f.read().replace('\n', ' ')
            analyzed_page = nlp_model(page)
            relations = extractor_of_entities(analyzed_page, common_words_limit, add_noun)
            total += len(relations)
            edges = edges + analyze_result(relations, art, edges_limit)

    return edges
