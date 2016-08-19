from django.shortcuts import render
from django.http import HttpResponse
from .models import Item


def front(request):
    item_list = Item.objects.order_by('-created')[:5]
    context = {'item_list':item_list}
    return render(request, 'shopping/front.html', context)

def front_template(request):
    item_list = Item.objects.order_by('-created')[:5]
    context = {'item_list':item_list}
    return render(request, 'shopping/index.html', context)


def item(request, item_id):
    fetched_item = Item.objects.get(id=item_id)
    return HttpResponse("%s"%fetched_item.name)