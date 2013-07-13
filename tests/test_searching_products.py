from os.path import join, pardir
import sys
import shutil
import unittest

sys.path.insert(0, join(pardir))
from prodcomp import Product, ProductRepository

test_database_path = 'testdb'

class TestBase(unittest.TestCase):

    def setUp(self):
        shutil.rmtree(test_database_path, ignore_errors=True)
        
    def create_product_with_url(self, product_url):
        return Product(url=product_url, \
                       title='heading text', \
                       price='10.00', \
                       description='product desc', \
                       image_url='image url')

    def create_product(self):
        return self.create_product_with_url('product url')

class SinglePageTests(TestBase):

    def setUp(self):
        super(SinglePageTests, self).setUp()
        self.repository = ProductRepository(test_database_path)

class NoProductsTest(SinglePageTests):

    def testItShouldReturnEmptyResult(self):
        result = self.repository.search('no such product')

        self.assertEquals(result.page_count, 0)
        self.assertEquals(result.products, [])

class OneProductTest(SinglePageTests):

    def testItShouldReturnMatchingProduct(self):
        expectedProduct = self.create_product_with_url('product url')

        self.repository.add_product(expectedProduct)

        result = self.repository.search('product')

        self.assertEquals(result.page_count, 1)
        self.assertEquals(len(result.products), 1)
    
        self.assertEquals(result.products[0], expectedProduct)

class ManyProductsTest(SinglePageTests):
    
    def testItShouldReturnManyProducts(self):
        product1 = self.create_product_with_url('product url')
        product2 = self.create_product_with_url('product2 url')

        self.repository.add_product(product1)
        self.repository.add_product(product2)

        result = self.repository.search('product')

        self.assertEquals(result.page_count, 1)
        self.assertEquals(len(result.products), 2)
    
        self.assertTrue(product1 in result.products)
        self.assertTrue(product2 in result.products)

class ManyPagesOfProductsTest(TestBase):

    def setUp(self):
        super(ManyPagesOfProductsTest, self).setUp()
        self.repository = ProductRepository(test_database_path, page_size = 1)

        self.product1 = self.create_product_with_url('product url')
        self.product2 = self.create_product_with_url('product2 url')
        self.repository.add_product(self.product1)
        self.repository.add_product(self.product2)

    def testItShouldReturnProducts(self):
        result = self.repository.search('product')

        self.assertEquals(result.page_count, 2)
        self.assertEquals(len(result.products), 1)

    def testItShouldReturnPage2Product(self):
        result = self.repository.search('product', 1)

        self.assertEquals(result.page_count, 2)
        self.assertEquals(len(result.products), 1)

    def testItReturnsProducts(self):
        result = self.repository.search('product', 0)
        page1_product = result.products[0]
        
        result = self.repository.search('product', 1)
        page2_product = result.products[0]
        
        self.assertFalse(page1_product == page2_product)

    def testItShouldReturnNoProductsFromPageThatDoesNotExists(self):
        result = self.repository.search('product', 2)        
        self.assertEquals(result.products, [])
        self.assertEquals(result.page_count, 0)


class ProductTitleAndDescriptionAreIndexedTest(SinglePageTests):

    def setUp(self):
        super(ProductTitleAndDescriptionAreIndexedTest, self).setUp()
        self.repository.add_product(self.create_product())

    def testItShouldFindProductFromTitleFirstWord(self):
        result = self.repository.search('heading')
        self.assertEquals(len(result.products), 1)

    def testItShouldFindProductFromTitleSecondWord(self):
        result = self.repository.search('text')
        self.assertEquals(len(result.products), 1)

    def testItShouldFindProductFromDescriptionsSecondWord(self):
        result = self.repository.search('desc')
        self.assertEquals(len(result.products), 1)



class OnlyCompleteMatchIsReturnedTest(SinglePageTests):

    def setUp(self):
        super(OnlyCompleteMatchIsReturnedTest, self).setUp()
        self.repository.add_product(self.create_product())

    def testItReturnsOnlyCompleteMatch(self):
        result = self.repository.search('heading text worm')
        self.assertEquals(len(result.products), 0)

    
# TODO: price sorting
# TODO: Support for many databases



if __name__ == '__main__':
    unittest.main()