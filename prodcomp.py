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
        database_path - Path to the database or list of database paths
        page_size - Number products on single page. Default is 10 products"""
        self._page_size = page_size or 10
        database_paths = database_path if isinstance(database_path, list) else [database_path]
            
        self._db = xapian.WritableDatabase()
        self._databases = {}
        self._add_databases_to_db(database_paths)
        

    def _add_databases_to_db(self, database_paths):
        for db_path in database_paths:
            database = self._create_or_open_database(db_path)
            self._databases[db_path] = database
            self._db.add_database(database)


    def _create_or_open_database(self, database_path):
        return xapian.WritableDatabase(database_path, xapian.DB_CREATE_OR_OPEN)
        
    def add_product(self, product, database_path=None):
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
        doc.add_value(0, xapian.sortable_serialise(float(product.price)))

        idterm = "Q" + product.url
        doc.add_boolean_term(idterm)

        db = self._db
        if database_path:
            db = self._databases[database_path]

        db.replace_document(idterm, doc)

    def add_products(self, products):
        """Add list of products to repository"""
        for product in products:
            self.add_product(product)

    def _create_stem(self):
        return xapian.Stem("fi")


    def search(self, search_words, page_index=None, sort_by_price=None):
        """Searches database with given words
        search_words - Search string
        page_index - from which page the results starts from. 0 is first page
        sort_by_price - Are products sorted by price or not.
        """
        page_index = page_index or 0
        sort_by_price = sort_by_price or False
        queryparser = xapian.QueryParser()
        queryparser.set_stemmer(self._create_stem())
        queryparser.set_stemming_strategy(queryparser.STEM_ALL)
  
        # And parse the query
        search_words = ' AND '.join(search_words.split())
        query = queryparser.parse_query(search_words)

        # Use an Enquire object on the database to run the query
        enquire = xapian.Enquire(self._db)
        enquire.set_query(query)
        if sort_by_price:
            enquire.set_sort_by_value(0, False)

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

