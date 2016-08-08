from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import models

class ItemTestCreateRemove(TestCase):
    def setUp(self):
        self.item = models.Item.objects.create(
            name='Test Item',
            stock=100,
            description='test test test ...',
            created = timezone.now(),
            RRP = 5.0,
        )
        
        
    def test_item_creation(self):
        self.assertEqual(len(models.Item.objects.all()), 1)
        self.assertEqual(models.Item.objects.all()[0], self.item)
        
    def test_item_removal(self):
        self.item.delete()
        self.assertEqual(len(models.Item.objects.all()), 0)



    def test_image_cascade_removal(self):
        # Create an image 
        p = SimpleUploadedFile(
            name='test_image.jpg', 
            content=open('images/soap__large.jpg', 'rb').read(), 
            content_type='image/jpeg'
        )
        self.item.image_set.create(
            name="example image", 
            picture=p
        )
        
        # Ensure image is removed
        self.item.delete()
        self.assertEqual(len(models.Image.objects.all()), 0)
        
    