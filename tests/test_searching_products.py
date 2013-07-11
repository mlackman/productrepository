from os.path import join, pardir
import sys
import shutil
import unittest

sys.path.insert(0, join(pardir))
from prodcomp import Product, ProductRepository

test_database_path = 'testdb'

class AcceptanceTestBase(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(test_database_path, ignore_errors=True)
        self.repository = ProductRepository(test_database_path)

class NoProductsAcceptanceTest(AcceptanceTestBase):


    def testItShouldReturnEmptyResult(self):
        result = self.repository.search('no such product')

        self.assertEquals(result.page_count, 0)
        self.assertEquals(result.products, [])

class OneProductAcceptanceTest(AcceptanceTestBase):

    def testItShouldReturnMatchingProduct(self):
        expectedProduct = Product(url='product url', \
                                  title='prodict title', \
                                  price='10.00', \
                                  description='product desc', \
                                  image_url='product image url')

        self.repository.add_product(expectedProduct)

        result = self.repository.search('product')

        self.assertEquals(result.page_count, 1)
        self.assertEquals(len(result.products), 1)
    
        self.assertEquals(result.products[0], expectedProduct)



if __name__ == '__main__':
    unittest.main()