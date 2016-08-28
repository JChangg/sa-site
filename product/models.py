from __future__ import unicode_literals
import os

from django.db import models, IntegrityError, DataError
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.db.models import F
import errors
import json

class Tag(models.Model):
    word = models.CharField(max_length=10)
    created = models.DateTimeField('Date created', auto_now=True)
    colour = models.CharField(max_length=6, default='000000')
    def __str__(self):
        return self.word
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        if not len(self.colour) == 6:
            raise DataError("HEX color code expected")
        super(Tag, self).save(*args, **kwargs)


class Promotion(models.Model):
    
    BUNDLE = 'b'
    VALUE = 'v'
    TYPES_OF_PROMO = (
        (BUNDLE, 'Bundle'),
        (VALUE, 'Value')
    )
    
    name = models.CharField(max_length=200)
    promo_type = models.CharField(
        max_length=1,
        choices=TYPES_OF_PROMO,
        default=BUNDLE
    )

    created = models.DateTimeField('Date created')
    expires = models.DateTimeField('Date expires')
    params = models.CharField(max_length=1000) #JSON OBJECT
    
    
    def __str__(self):
        return self.name
    
    
    def get_params(self):
        return json.loads(self.params)
    
    def set_params(self, params):
        return json.dumps(params)
    
    def save(self, *args, **kwargs):
        if self.created <= self.expires:
            super(Promotion, self).save(*args, **kwargs)
        else:
            raise DataError("Must expire after creation")


        
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    stock = models.IntegerField(default=0)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField('Date created')
    RRP = models.FloatField()
    price = models.FloatField()
    tags = models.ManyToManyField(
        Tag, 
        blank=True
    )
    promotion = models.ManyToManyField(
        Promotion, 
        blank=True,
    )
    
    SMALL = 'sm'
    MEDIUM = 'md'
    LARGE = 'lg'
    
    SIZE_CHOICES = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'large')
    )
    
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default=SMALL)
    
    def __str__(self):
        return self.name
        
    def out_of_stock(self):
        return self.stock <= 0
    
    def sell(self, num=1):
        if self.stock < num:
            raise errors.NotEnoughStockException(self.stock, num)
        else:
            self.stock = F('stock') - num
            self.save()
        
    def add(self, num):
        self.stock = F('stock') + num
        self.save()
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.RRP
        super(Product, self).save(*args, **kwargs)

    
class Image(models.Model):
    name = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=settings.SHOPPING_DIR)
    
    def __str__(self):
        return self.name

class Thumbnail(models.Model):
    picture = models.ForeignKey(Image)
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    
    def __str__(self):
        return self.picture.__str__()
    
    def save(self, *args, **kwargs):
        if self.product == self.picture.product:
            super(Thumbnail, self).save(*args, **kwargs)
        else:
            exp_txt = "Thumbnail should belong to the same object"
            raise IntegrityError(exp_txt)
            

# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=Image)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Image` object is deleted.
    """
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)

@receiver(models.signals.pre_save, sender=Image)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Image` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = Image.objects.get(pk=instance.pk).picture
    except Image.DoesNotExist:
        return False

    new_file = instance.picture
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)