import xapian
import json

class SearchResult(object):
    
    def __init__(self):
        self.page_count = 0
        self.products = []   

class Product(object):

    def __init__(self, title, url, image_url, description, price):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.description = description
        self.price = price

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ProductRepository(object):

    def __init__(self, database_path, page_size = None):
        """Construcst ProductRepository
        database_path - Path to the database
        page_size - Number products on single page"""
        self._db = xapian.WritableDatabase(database_path, xapian.DB_CREATE_OR_OPEN)
        self._page_size = page_size or 10
        
    def add_product(self, product):
        """Adds product to repository"""
        # Set up a TermGenerator that we'll use in indexing.
        termgenerator = xapian.TermGenerator()
        termgenerator.set_stemmer(self._create_stem())

        # We make a document and tell the term generator to use this.
        doc = xapian.Document()
        termgenerator.set_document(doc)
        termgenerator.index_text(unicode(product.title))
        termgenerator.index_text(unicode(product.description))
        doc.set_data(unicode(json.dumps(product.__dict__)))
        idterm = "Q" + product.url
        doc.add_boolean_term(idterm)
        self._db.replace_document(idterm, doc)

    def _create_stem(self):
        return xapian.Stem("fi")


    def search(self, search_words, page_index=None):
        """Searches database with given words
        search_words - Search string
        page_index - from which page the results starts from. 0 is first page"""
        page_index = page_index or 0
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(self._create_stem())
        queryparser.set_stemming_strategy(queryparser.STEM_ALL)
  
        # And parse the query
        query = queryparser.parse_query(search_words)

        # Use an Enquire object on the database to run the query
        enquire = xapian.Enquire(self._db)
        enquire.set_query(query)

        offset = page_index * self._page_size
        matches = enquire.get_mset(offset, self._page_size)
        result = SearchResult()
        result.page_count = self._get_page_count(matches)
        
        for match in matches:
            product = self._create_product(match)
            result.products.append(product)
        return result

    def _create_product(self, match):
        return Product(**json.loads(match.document.get_data()))

    def _get_page_count(self, matches):
        page_count = 0
        estimated_matches = int(matches.get_matches_estimated())
        if len(matches) > 0:
            if estimated_matches >= self._page_size:
                page_count = estimated_matches / self._page_size
            else:
                page_count = 1
        return page_count

