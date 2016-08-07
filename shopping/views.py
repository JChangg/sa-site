from django.shortcuts import render
from django.http import HttpResponse

def front(request):
    return HttpResponse("Hello")
