import os

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import models, errors
from django.db import IntegrityError



class ItemAbstractTestCase:
    ''' Abstract class that initiates a new item in the database
    Inherit this to instantiate a new item in setup
    '''
    
    def setUp(self):
        self.item = models.Item.objects.create(
            name='Test Item',
            stock=100,
            description='test test test ...',
            created = timezone.now(),
            RRP = 5.0,
        )


class ImageAbstractTestCase(ItemAbstractTestCase):
    ''' Abstract class that initiates a new image in the database
    Inherit this to instantiate a new image and item in setup
    '''
    
    def setUp(self):
        ItemAbstractTestCase.setUp(self)
        mock_img = SimpleUploadedFile(
            name='__test_image__.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        self.image = models.Image.objects.create(
            name="example image", 
            picture=mock_img,
            item=self.item
        )
        self.fpath = settings.SHOPPING_DIR

        
    def tearDown(self):
        fpath = self.fpath
        for f in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, f)):
                if f.startswith('__test_image__'):
                    os.remove(os.path.join(fpath, f))


class ItemTestCase(ItemAbstractTestCase, TestCase):
        
    def test_item_creation(self):
        self.assertEqual(len(models.Item.objects.all()), 1)
        self.assertEqual(models.Item.objects.all()[0], self.item)
        
    def test_item_removal(self):
        self.item.delete()
        with self.assertRaises(models.Item.DoesNotExist):
            self.item.refresh_from_db()
    
    def test_item_stock_function(self):
        self.assertEqual(self.item.out_of_stock(), False)
        self.item.sell(100)
        self.item.refresh_from_db()        
        self.assertEqual(self.item.out_of_stock(), True)
        
    def test_item_over_sell(self):
        with self.assertRaises(errors.NotEnoughStockException):
            self.item.sell(500)
            
    def test_item_stock_add(self):
        self.item.sell(100)
        self.item.refresh_from_db()
        self.assertEqual(self.item.out_of_stock(), True)
        self.item.add(100)
        self.item.refresh_from_db()
        self.assertEqual(self.item.out_of_stock(), False)


class ImageTestCase(ImageAbstractTestCase, TestCase):
    
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        TestCase.setUp(self)
        self.fpath = settings.SHOPPING_DIR
    
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
    
    def test_item_thumbnail_cascade_removal(self):
        self.item.delete()
        with self.assertRaises(models.Thumbnail.DoesNotExist):
            self.thumbnail.refresh_from_db()
        
        
    def test_thumbnail_picture_incorrect_item(self):
        ''' Test whether or not an incorrect image 
        can be assigned to the item as a thumbnail
        '''
        item2 = models.Item.objects.create(
            name='Test Item 2',
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
            item=self.item
        )
        with self.assertRaises(IntegrityError):
            models.Thumbnail.objects.create(
                picture=image2,
                item=self.item
            )
            
class PromotionTestCase(ImageAbstractTestCase, TestCase):
    pass


class TagTestCase(ImageAbstractTestCase, TestCase):
    pass