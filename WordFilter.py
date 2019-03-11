"""
Filter words that does not match our wishes
"""
import string
printable = set(string.printable)  # for ascii-only chars filter
# Module downloads and load
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except:
    import nltk
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))


from nltk.stem import PorterStemmer

ps = PorterStemmer()
ARTICLE_COMMON_WORDS = ["figure", "example", "Ms.", "Mr."]


class WordFilter:
    """
    Class that filter words, using filter_word()
    """
    def __init__(self, common_words_limit, to_filter_relations):
        self.common_words = self.get_common_words(common_words_limit)
        self.filter_relations = to_filter_relations

    def filter_word(self, word_arg):
        """
        Filter not ascii words, numbers, common words, words that do not contain letters/numbers
        :param word_arg: the candidate if to filter or not
        :return: true if not to filter, false otherwise
        """
        for word in word_arg.split(" "):
            if len(list(filter(lambda x: x not in printable, word))) > 0:  # filter non-ascii words
                return False
            if word.isdigit():
                return False
            if not word.isalnum():  # filter non-alpha-numeric words
                return False
            # word = ps.stem(word)                                  # stemming the alphanumeric word
            if word in stop_words:  # filter english stopwords
                return False
            if word in ARTICLE_COMMON_WORDS:  # filter common words in articles
                return False
            if word in self.common_words and self.filter_relations:
                return False
        return True

    @staticmethod
    def get_common_words(limit=1000):
        """
        The most 5000 common words in English
        :param limit: the amount we want to use from the document
        :return: a list size #limit with the top #limit commom words
        """
        with open("data/commonwords.csv", "r", encoding="utf-8") as f:
            common_words = f.readlines()[:limit]
            common_words = [word.split(",")[1].strip(" ") for word in common_words if "," in word]
            return common_words
