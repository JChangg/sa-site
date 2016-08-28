import os

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import models, errors
from django.core.exceptions import ValidationError
from django.db import IntegrityError


#ABSTRACT CLASSES

class ProductAbstractTestCase:
    ''' Abstract class that initiates a new product in the database
    Inherit this to instantiate a new product in setup
    '''
    
    def setUp(self):
        self.product = models.Product.objects.create(
            name='Test Product',
            description='test test test ...',
            created = timezone.now(),
        )

class ItemAbstractTestCase(ProductAbstractTestCase):
    ''' Abstract class that initiates a new Item in the database
    using the initialized product. Inherit this to instantiate a
    new item in setup
    '''
    
    def setUp(self):
        ProductAbstractTestCase.setUp(self)
        self.item = models.Item.objects.create(
            stock=100,
            description='weighs 100g',
            RRP = 5.0,
            price = 2.5,
            product = self.product
        )


class ImageAbstractTestCase(ItemAbstractTestCase):
    ''' Abstract class that initiates a new image in the database
    Inherit this to instantiate a new image in setup
    '''
    
    def setUp(self):
        ItemAbstractTestCase.setUp(self)
        mock_img = SimpleUploadedFile(
            name='__test_image__.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        self.image = models.Image.objects.create(
            picture=mock_img,
            item=self.item
        )
        self.fpath = settings.SHOPPING_DIR + settings.MEDIA_ROOT

        
    def tearDown(self):
        fpath = self.fpath
        for f in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, f)):
                if f.startswith('__test_image__'):
                    os.remove(os.path.join(fpath, f))



################################################################################


# Test Cases
class ProductTestCase(ProductAbstractTestCase, TestCase):
    
    def test_product_str_fucntion(self):
        ''' Tests whether the __str__ function returns name
        '''
        self.assertEqual(self.product.__str__(), self.product.name)
    def test_product_catagory_removal(self):
        ''' Tests if removing catagory does *NOT* remove products
        '''
        catagory = self.product.catagories.create(
            name="Test Catagory",
            description="Test Catagory for test products"
        )
        catagory.delete()
        self.product.refresh_from_db()
        self.assertEqual(len(models.Product.objects.all()), 1)
        

class ItemTestCase(ItemAbstractTestCase, TestCase):
        
    def test_item_save(self):
        ''' Tests the custom save functionality
        '''
        item = models.Item.objects.create(
            stock=100,
            description='weighs 100g',
            RRP = 2.5,
            product = self.product,
            size = models.Item.MEDIUM
        )
        self.assertEqual(item.price, item.RRP)
        
    def test_item_stock_function(self):
        ''' Tests that the out_of_stock function of item functions correctly
        '''
        self.assertEqual(self.item.out_of_stock(), False)
        self.item.sell(100)
        self.item.refresh_from_db()        
        self.assertEqual(self.item.out_of_stock(), True)
        
    def test_item_over_sell(self):
        ''' Tests that the sell function of item functions correctly
        '''
        with self.assertRaises(errors.NotEnoughStockException):
            self.item.sell(500)
            
    def test_item_stock_add(self):
        ''' Tests that the add function behaves correctly
        '''
        self.item.sell(100)
        self.item.refresh_from_db()
        self.assertEqual(self.item.out_of_stock(), True)
        self.item.add(100)
        self.item.refresh_from_db()
        self.assertEqual(self.item.out_of_stock(), False)

    def test_item_str_fucntion(self):
        ''' Tests whether the __str__ function returns name
        '''
        self.assertEqual(self.item.__str__(), self.product.name 
            + '_' + self.item.size)
    
    def test_item_size_choices(self):
        self.assertEqual(self.item.size, self.item.SMALL)
        with self.assertRaises(ValidationError):
            self.item.size = 'jk'
            self.item.save()
            
            
    def test_item_size_unique(self):
        with self.assertRaises(Exception):
            models.Item.objects.create(
                name='Test Item 2',
                stock=100,
                description='weighs 100g',
                RRP = 5.0,
                price = 2.5,
                product = self.product
            )
        

class ImageTestCase(ImageAbstractTestCase, TestCase):
    
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        TestCase.setUp(self)

    def test_image_reference_removal(self):
        self.image.delete()
        with self.assertRaises(models.Image.DoesNotExist):
            self.image.refresh_from_db()
        
    
    def test_image_file_removal(self):
        self.image.delete()
        fpath = self.fpath
        files = [f for f in os.listdir(fpath) 
            if os.path.isfile(os.path.join(fpath, f))]
        self.assertEqual(len(files), 0)
        
    def test_item_image_cascade_removal(self):
        # Ensure image is removed
        self.item.delete()
        with self.assertRaises(models.Image.DoesNotExist):
            self.image.refresh_from_db()
        
        
class ThumbnailTestCase(ImageAbstractTestCase, TestCase):
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        self.thumbnail = models.Thumbnail.objects.create(
            picture=self.image,
            item=self.item
        )
    
    def test_product_thumbnail_cascade_removal(self):
        self.product.delete()
        with self.assertRaises(models.Thumbnail.DoesNotExist):
            self.thumbnail.refresh_from_db()
        
        
    def test_thumbnail_picture_incorrect_product(self):
        ''' Test whether or not an incorrect image 
        can be assigned to the product as a thumbnail
        '''
        item2 = models.Item.objects.create(
            product=self.product,
            description='test test test ...',
            created = timezone.now(),
            stock=100,
            RRP=50,
            size=models.Item.MEDIUM
        )
        mock_img = SimpleUploadedFile(
            name='__test_image__.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        image2 = models.Image.objects.create(
            picture=mock_img,
            item=item2
        )
        with self.assertRaises(IntegrityError):
            models.Thumbnail.objects.create(
                picture=image2,
                item=self.item
            )
            
            
class CatagoryTestCase(ProductAbstractTestCase, TestCase):
    def setUp(self):
        ProductAbstractTestCase.setUp(self)
        self.catagory = self.product.catagories.create(
            name="Test Catagory",
            description="Test Catagory for test products"
        )
        
    def test_multi_catagory(self):
        ''' test 2 catagories can be added to a product
        '''
        catagory2 = self.product.catagories.create(
            name="Test Cataory 2",
            description="Blah Blah"
        )
        self.assertEqual(len(self.product.catagories.all()), 2)
        
    
            
class PromotionTestCase(ImageAbstractTestCase, TestCase):
    pass


class TagTestCase(ImageAbstractTestCase, TestCase):
    pass