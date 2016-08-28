import os

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import models, errors
from django.db import IntegrityError



class ProductAbstractTestCase:
    ''' Abstract class that initiates a new product in the database
    Inherit this to instantiate a new product in setup
    '''
    
    def setUp(self):
        self.product = models.Product.objects.create(
            name='Test Product',
            stock=100,
            description='test test test ...',
            created = timezone.now(),
            RRP = 5.0,
        )


class ImageAbstractTestCase(ProductAbstractTestCase):
    ''' Abstract class that initiates a new image in the database
    Inherit this to instantiate a new image and product in setup
    '''
    
    def setUp(self):
        ProductAbstractTestCase.setUp(self)
        mock_img = SimpleUploadedFile(
            name='__test_image__.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        self.image = models.Image.objects.create(
            name="example image", 
            picture=mock_img,
            product=self.product
        )
        self.fpath = settings.SHOPPING_DIR + settings.MEDIA_ROOT

        
    def tearDown(self):
        fpath = self.fpath
        for f in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, f)):
                if f.startswith('__test_image__'):
                    os.remove(os.path.join(fpath, f))


class ProductTestCase(ProductAbstractTestCase, TestCase):
        
    def test_product_creation(self):
        self.assertEqual(len(models.Product.objects.all()), 1)
        self.assertEqual(models.Product.objects.all()[0], self.product)
        
    def test_product_removal(self):
        self.product.delete()
        with self.assertRaises(models.Product.DoesNotExist):
            self.product.refresh_from_db()
    
    def test_product_stock_function(self):
        self.assertEqual(self.product.out_of_stock(), False)
        self.product.sell(100)
        self.product.refresh_from_db()        
        self.assertEqual(self.product.out_of_stock(), True)
        
    def test_product_over_sell(self):
        with self.assertRaises(errors.NotEnoughStockException):
            self.product.sell(500)
            
    def test_product_stock_add(self):
        self.product.sell(100)
        self.product.refresh_from_db()
        self.assertEqual(self.product.out_of_stock(), True)
        self.product.add(100)
        self.product.refresh_from_db()
        self.assertEqual(self.product.out_of_stock(), False)


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
        
    def test_product_image_cascade_removal(self):
        # Ensure image is removed
        self.product.delete()
        with self.assertRaises(models.Image.DoesNotExist):
            self.image.refresh_from_db()
        
        
class ThumbnailTestCase(ImageAbstractTestCase, TestCase):
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        self.thumbnail = models.Thumbnail.objects.create(
            picture=self.image,
            product=self.product
        )
    
    def test_product_thumbnail_cascade_removal(self):
        self.product.delete()
        with self.assertRaises(models.Thumbnail.DoesNotExist):
            self.thumbnail.refresh_from_db()
        
        
    def test_thumbnail_picture_incorrect_product(self):
        ''' Test whether or not an incorrect image 
        can be assigned to the product as a thumbnail
        '''
        product2 = models.Product.objects.create(
            name='Test Product 2',
            stock=100,
            description='test test test ...',
            created = timezone.now(),
            RRP = 5.0,
        )
        mock_img = SimpleUploadedFile(
            name='__test_image__.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        image2 = models.Image.objects.create(
            name="example image", 
            picture=mock_img,
            product=self.product
        )
        with self.assertRaises(IntegrityError):
            models.Thumbnail.objects.create(
                picture=image2,
                product=self.product
            )
            
class PromotionTestCase(ImageAbstractTestCase, TestCase):
    pass


class TagTestCase(ImageAbstractTestCase, TestCase):
    pass