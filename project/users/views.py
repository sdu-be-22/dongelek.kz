from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from . forms import UserRegisterForm

# Create your views here.
def home(request):
    return render(request,'users/layout.html')


def register(request):
    if request.method =='POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Hi {username}, your account was created succesfully' )
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request,'users/register.html',{
        'form':form
    })
