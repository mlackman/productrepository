from os.path import join, pardir
import sys
import unittest

sys.path.insert(0, join(pardir))
from prodcomp import ProductCompare

test_database_path = 'testdb'


class NoProductsAcceptanceTest(unittest.TestCase):

    def testItShouldReturnEmptyResult(self):

        pc = ProductCompare(test_database_path)
        result = pc.search('no such product')

        self.assertEquals(result.page_count, 0)
        self.assertEquals(result.products, [])

if __name__ == '__main__':
    unittest.main()