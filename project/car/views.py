from django.http import HttpResponse
from django.shortcuts import render
from car.models import Person

# Create your views here.
def index(request):
    names = Person.objects.all()
    return render(request,'car/layout.html',{
        'names':names
    })