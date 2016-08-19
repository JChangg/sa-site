import os

from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import models



class ItemAbstractTestCase:
    
    def setUp(self):
        self.item = models.Item.objects.create(
            name='Test Item',
            stock=100,
            description='test test test ...',
            created = timezone.now(),
            RRP = 5.0,
        )


class ImageAbstractTestCase(ItemAbstractTestCase):
    
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


class ItemTestCase(ItemAbstractTestCase, TestCase):
        
    def test_item_creation(self):
        self.assertEqual(len(models.Item.objects.all()), 1)
        self.assertEqual(models.Item.objects.all()[0], self.item)
        
    def test_item_removal(self):
        self.item.delete()
        self.assertEqual(len(models.Item.objects.all()), 0)
    
    def test_item_stock_function(self):
        self.assertEqual(self.item.out_of_stock(), False)
        self.item.stock = 0
        self.assertEqual(self.item.out_of_stock(), True)
    
    '''    
    def test_thumbnail_create_removal(self):
        p = SimpleUploadedFile(
            name='test_image.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        img = self.item.image_set.create(
            name="example image", 
            picture=p
        )
        thumb = models.Thumbnail.objects.create(
            item=self.item,
            picture=img
        )
        
        self.item.delete()
        self.assertEqual(len(models.Thumbnail.objects.all()), 0)
    '''

class ImageTestCase(ImageAbstractTestCase, TestCase):
    
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        TestCase.setUp(self)
        self.fpath = settings.SHOPPING_DIR
    
    def tearDown(self):
        fpath = self.fpath
        for f in os.listdir(fpath):
            if os.path.isfile(os.path.join(fpath, f)):
                if f.startswith('__test_image__'):
                    os.remove(os.path.join(fpath, f))
                    
    def test_image_reference_removal(self):
        self.image.delete()
        self.assertEqual(len(self.item.image_set.all()), 0)
    
    def test_image_file_removal(self):
        self.image.delete()
        fpath = self.fpath
        files = [f for f in os.listdir(fpath) 
            if os.path.isfile(os.path.join(fpath, f))]
        self.assertEqual(len(files), 0)
        
    def test_item_image_cascade_removal(self):
        
        # Ensure image is removed
        self.item.delete()
        self.assertEqual(len(models.Image.objects.all()), 0)
        
        
class ThumbnailTestCase(ImageAbstractTestCase, TestCase):
    def setUp(self):
        ImageAbstractTestCase.setUp(self)
        models.Thumbnail.objects.create(
            picture=self.image,
            item=self.item
        )
        
    