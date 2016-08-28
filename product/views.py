from django.shortcuts import render
from django.http import HttpResponse
from .models import Product


def front(request):
    product_list = Product.objects.order_by('-created')[:5]
    context = {'product_list':product_list}
    return render(request, 'product/index.html', context)

