from django.shortcuts import render
from django.http import HttpResponse
from .models import Item


def front(request):
    item_list = Item.objects.order_by('-created')[:5]
    context = {'item_list':item_list}
    return render(request, 'product/index.html', context)

