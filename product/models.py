from __future__ import unicode_literals
import os

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.dispatch import receiver
from django.db.models import F
import errors
import json
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from easy_thumbnails.fields import ThumbnailerImageField





# Validators
def validate_non_zero(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s is negative'),
            params={'value': value},
        )


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
            raise ValidationError("HEX color code expected")
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
        if self.created > self.expires:
            raise ValidationError("Must expire after creation")
        elif self.promo_type not in dict(Promotion.TYPES_OF_PROMO):
            raise ValidationError("Must choose from item set.")
        else:
            super(Promotion, self).save(*args, **kwargs)
    

class Catagory(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField('Date created')
    tags = models.ManyToManyField(Tag, blank=True)
    catagories = models.ManyToManyField(Catagory, blank=True)

    def __str__(self):
        return self.name
        


class Item(models.Model):
    SMALL = 'sm'
    MEDIUM = 'md'
    LARGE = 'lg'
    
    SIZE_CHOICES = (
        (SMALL, 'Small'),
        (MEDIUM, 'Medium'),
        (LARGE, 'Large')
    )

    # useful fields
    description = models.CharField(max_length=1000)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    RRP = models.DecimalField(
        decimal_places=2, 
        max_digits=10, 
        validators=[validate_non_zero]
    )
    price = models.DecimalField(
        decimal_places=2, 
        max_digits=10, 
        validators=[validate_non_zero]
    )
    created = models.DateTimeField(auto_now=True)
    stock = models.IntegerField(default=0, validators=[validate_non_zero])
    size = models.CharField(max_length=2, choices=SIZE_CHOICES, default=SMALL)

    promotion = models.ManyToManyField(
        Promotion, 
        blank=True,
    )
    
    
    class Meta:
        unique_together = (("product", "size"),)
    

    def save(self, *args, **kwargs):
        if self.size not in dict(Item.SIZE_CHOICES):
            raise ValidationError('Invalid size')
        if not self.description:
            self.description=self.product.description
        if not self.price:
            self.price = self.RRP
        super(Item, self).save(*args, **kwargs)
    
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

    def __str__(self):
        return self.product.name + '_' + self.size
        

class Image(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    picture = ThumbnailerImageField(upload_to=settings.SHOPPING_DIR)
    
    def __str__(self):
        return self.picture.name


class Thumbnail(models.Model):
    picture = models.ForeignKey(
        Image, 
        on_delete=models.CASCADE
    )
    item = models.OneToOneField(
        Item, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    
    
    def __str__(self):
        return self.picture.__str__()
    
    def save(self, *args, **kwargs):
        if self.item == self.picture.item:
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