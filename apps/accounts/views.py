from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

def login_view(request):
    if request.method =="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("user_dashboard")
        else:
            return render(request, "login.html",{"error": "Invalid credentials"})
    
    return render(request,"login.html")

@login_required
def user_dashboard(request):
    
    return render(request,"dashboard.html")

def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            return render(request, "accounts/register.html", {
                "error": "Email already exists"
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role = 'user'
        )
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return redirect("login")
    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect("login")
