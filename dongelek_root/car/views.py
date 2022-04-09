from django.contrib import messages
from django.shortcuts import *
from django.http import HttpRequest, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from car.models import *
from .forms import *
from django.core.mail import send_mail
from dongelek.settings import EMAIL_HOST_USER
import os.path
import requests
import json


from urllib.request import urlopen
from django.shortcuts import render,redirect


# Create your views here.

menu = [
    {'title': "About site",
     'url_name': 'about'},
]


# Index home page
def index(request):
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = urlopen(url)
    data_json = json.loads(response.read())
    for v_id, v_info in data_json['Valute'].items():
        Valute.objects.filter(id=v_info["ID"]).update(id=v_info["ID"], num_code=v_info["NumCode"],
                              char_code=v_info["CharCode"], nominal=v_info["Nominal"],
                              name=v_info["Name"], value=v_info["Value"], previous=v_info["Previous"])
    brands = Brand.objects.all()
    cities = City.objects.all()
    valutes = Valute.objects.all()
    context = {
        'title': "Main Page",
        'menu': menu,
        'brands': brands,
        'cities': cities,
        'valutes': valutes,
    }
    return render(request, 'car/index.html', context)

# Registration 
def register_request(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('login')
    return render(request, 'car/register.html', {
        'form': form
    })


# Login
def login_request(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    else:
        return render(request, 'car/login.html')

    # Logout


def logout_request(request):
    logout(request)
    return redirect('home')


# About
def about(request):
    valutes = Valute.objects.all()
    context = {
        'title': "About",
        'menu': menu,
        'valutes': valutes,
    }
    return render(request, 'car/about.html', context)


# Profile
def profile(request):
    cars = Car.objects.filter(seller=request.user)
    valutes = Valute.objects.all()
    context = {
        'title': 'My profile',
        'menu': menu,
        'cars': cars,
        'valutes': valutes,
        'seller':request.user
    }
    return render(request, 'car/profile.html', context)


# add_car
def add_car(request):
    valutes = Valute.objects.all()
    if request.method == 'POST':
        form = AddCar(request.POST, request.FILES)
        if form.is_valid():
            try:
                Car.objects.create(**form.cleaned_data, seller=request.user)
                return redirect('home')
            except:
                form.add_error(None, "There are some errors")
    else:
        form = AddCar()
    context = {
        'title': "Add a new ad",
        'menu': menu,
        'form': form,
        'valutes': valutes,
    }
    return render(request, 'car/addCar.html', context)


def brand(request, brand_slug):
    valutes = Valute.objects.all()
    chosen_brand = Brand.objects.get(slug=brand_slug)
    cars = Car.objects.filter(brand_id=chosen_brand.pk)
    context = {
        'title': chosen_brand.name,
        'menu': menu,
        'cars': cars,
        'valutes': valutes,
        'brand': chosen_brand
    }

    return render(request, 'car/brand.html', context)


def city(request, city_slug):
    valutes = Valute.objects.all()
    city = City.objects.get(slug=city_slug)
    cars = Car.objects.filter(city_id=city.pk)
    context = {
        'valutes': valutes,
        'title': city.name,
        'menu': menu,
        'cars': cars,
        'brand': city
    }
    return render(request, 'car/brand.html', context)

def cart(request):
    valutes = Valute.objects.all()
    cars = Cart.objects.filter(user=request.user)
    context = {
        'valutes': valutes,
        'title': 'Your cart',
        'menu': menu,
        'cars': cars,
    }
    return render(request, 'car/cart.html', context)


def car(request, car_slug):
    valutes = Valute.objects.all()
    car = Car.objects.get(slug=car_slug)
    photos = Car_photos.objects.filter(car=car)
    seller = User.objects.get(pk=car.seller.pk)
    if request.user.is_authenticated and car.seller != request.user:
        Visits(car=car, visiter=request.user).save()
    comments = Comments.objects.filter(car=car).order_by('-pk')
    if request.method == 'POST':
        form = AddComment(request.POST)
        if form.is_valid():
            try:
                Comments.objects.create(**form.cleaned_data, author=request.user, car=car)
                return redirect(car.get_absolute_url)
            except:
                form.add_error(None, "There are some errors")
        form = AddComment()
    else:
        form = AddComment()
    context = {
        'title': car.name,
        'valutes': valutes,
        'menu': menu,
        'form': form,
        'seller': seller,
        'comments': comments,
        'car': car,
        'photos': photos,
    }
    cart = Cart.objects.filter(car=car.pk, user=request.user.pk)
    if len(cart) > 0:
        context['cart'] = True
    else:
        context['cart'] = False
    if car.get_average_rating() == 0:
        context['rating'] = False
    else:
        context['rating'] = car.get_average_rating()
    return render(request, 'car/car.html', context)


def rate_car(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        car_id = request.POST.get('car')
        car = Car.objects.get(pk=car_id)
        rater = request.user
        Ratings.objects.filter(car=car, rater=rater).delete()
        Ratings.objects.create(rating=rating, car=car, rater=rater).save()
        return JsonResponse({'success': 'true', 'score': rating}, safe=False)
    return JsonResponse({'success:': 'false'})


def add_to_cart(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_basket')
        car = Car.objects.get(pk=car_id)
        user = request.user
        Cart.objects.filter(car=car, user=user).delete()
        Cart.objects.create(car=car, user=user).save()
        return JsonResponse({'success': 'true'})
    return JsonResponse({'success:': 'false'})


def delete_from_cart(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_basket')
        car = Car.objects.get(pk=car_id)
        user = request.user
        Cart.objects.filter(car=car, user=user).delete()
        return JsonResponse({'success': 'true'})
    return JsonResponse({'success:': 'false'})


def delete_car(request):
    if request.method == 'POST':
        car_id = request.POST.get('car')
        car = Car.objects.filter(pk=car_id).delete()
        print(car)
        return JsonResponse({'success': 'true'})
    return JsonResponse({'success:': 'false'})


def send_email(request):
    if request.method == 'POST':
        car_id = request.POST.get('car_interested')
        car = Car.objects.get(pk=car_id)
        seller_email = request.POST.get('seller_email')
        seller_username = request.POST.get('seller_username')
        subject = 'Someone is interested to your car '
        message = request.user.username + " ( " + request.user.email + " )" + " is interested  to your " + str(car)
        send_mail(subject, message,
                  EMAIL_HOST_USER, [seller_email], fail_silently=False)
        subject = "From Dongelek.kz"
        message = "You've interested to " + str(car) + ". Wait answer from " + seller_username
        send_mail(subject, message,
                  EMAIL_HOST_USER, [request.user.email], fail_silently=False)
        return JsonResponse({'success': 'true'})
    return JsonResponse({'success:': 'false'})


def update_car(request, car_slug):
    car = Car.objects.get(slug=car_slug)
    if request.method == 'POST':
        form = AddCar(request.POST, request.FILES)
        if form.is_valid():
            try:
                os.remove(car.main_image.path)
                car.name = form.cleaned_data['name']
                car.slug = form.cleaned_data['slug']
                car.year = form.cleaned_data['year']
                car.engine_capacity = form.cleaned_data['engine_capacity']
                car.run = form.cleaned_data['run']
                car.color = form.cleaned_data['color']
                car.city = form.cleaned_data['city']
                car.brand = form.cleaned_data['brand']
                car.main_image = form.cleaned_data['main_image']
                car.price = form.cleaned_data['price']
                car.description = form.cleaned_data['description']
                car.save()
                return redirect('profile')
            except:
                form.add_error(None, "There are some errors")
    form = CarForm(instance=car)
    valutes = Valute.objects.all()
    context = {
        'valutes': valutes,
        'title': "Updating data about " + car.name,
        'menu': menu,
        'car': car,
        'form': form,
        'car': car,
    }
    if car.seller == request.user:
        return render(request, 'car/update.html', context)
    return render(request, 'car/index.html', context)


def add_photos_car(request, car_slug):
    car = Car.objects.get(slug=car_slug)
    if request.method == 'POST':
        form = PhotosForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        for image in files:
            Car_photos.objects.create(car=car, image=image).save()
        return redirect('profile')
    else:
        form = PhotosForm()
    valutes = Valute.objects.all()
    context = {
        'valutes': valutes,
        'title': "Add new photos",
        'menu': menu,
        'form': form,
        'car': car,
    }
    return render(request, 'car/addPhotos.html', context)


def searchbar(request):
    if request.method == 'GET':
        search = request.GET.get('search')
        post = Car.objects.all().filter(name=search)
        return render(request, 'car/searchbar.html', {'post': post})
