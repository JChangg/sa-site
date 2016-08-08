from django.contrib import admin
from . import models


class ThumbnailInline(admin.TabularInline):
    model = models.Thumbnail


class ImageInline(admin.TabularInline):
    model = models.Image
    extra = 3

class ItemAdmin(admin.ModelAdmin):
    inlines = [ThumbnailInline, ImageInline]

admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Promotion)