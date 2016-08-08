from __future__ import unicode_literals

from django.db import models

class Tag(models.Model):
    word = models.CharField(max_length=10)
    created = models.DateTimeField('Date created')
    def __str__(self):
        return self.word

class Promotion(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField('Date created')
    expires = models.DateTimeField('Date expires')
    
    def __str__(self):
        return self.name
    
    def remaining_time(self):
        return self.expires - self.created
        
    
class Item(models.Model):
    name = models.CharField(max_length=200)
    stock = models.IntegerField(default=0)
    description = models.CharField(max_length=1000)
    created = models.DateTimeField('Date created')
    RRP = models.FloatField()
    tags = models.ManyToManyField(
        Tag, 
        related_name='items_tagged', 
        blank=True
    )
    promotion = models.ManyToManyField(
        Promotion, 
        related_name='items_promoted', 
        blank=True,
    )
    def __str__(self):
        return self.name
        
    def out_of_stock(self):
        return self.stock <= 0

        
class Image(models.Model):
    name = models.CharField(max_length=200)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="images")
    def __str__(self):
        return self.name


class Thumbnail(models.Model):
    picture = models.ForeignKey(Image)
    item = models.OneToOneField(
        Item, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    def __str__(self):
        return self.picture.__str__()
    
