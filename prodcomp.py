
class SearchResult(object):
    
    def __init__(self):
        self.page_count = 0
        self.products = []


class ProductCompare(object):

    def __init__(self, database_path):
        """Constructs ProductCompare object.
        database_path - Path to the database"""
        pass

    def search(self, search_words):
        """Searches database with given words
        search_words - Search string"""
        return SearchResult()