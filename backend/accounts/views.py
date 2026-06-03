from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
        return render(request, 'login.html', {'error': 'Invalid username or password.'})
    return render(request, 'login.html')

def signup_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        email = request.POST.get('email','').strip()
        password = request.POST.get('password','').strip()
        confirm = request.POST.get('confirm','').strip()
        if password != confirm:
            return render(request, 'signup.html', {'error': 'Passwords do not match.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already taken.'})
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('/login/')
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def dashboard_page(request):
    return render(request, 'dashboard.html', {'user': request.user})
