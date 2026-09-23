from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import login
from django.contrib.auth.models import User



def signup_page(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            print("FORM DATA : ",form.cleaned_data)
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_superuser = False
            user.is_staff = False
            user.is_active = True
            user.save()
            return redirect("login")
    else:
        form = SignupForm()
    return render(request,"members/signup.html",{"form": form})


def login_page(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            print("FORM DATA : ", form.cleaned_data)
            user = form.cleaned_data["user"]
            login(request, user)
            return redirect("main")
    else:
        form = LoginForm()
    return render(request, "members/login.html", {"form": form})


def show_users(request):
    user_data = User.objects.all()
    return render(request, "members/users_data.html", {"users": user_data})


def forgot_password(request):
    return render(request, "members/forgot_password.html")


# def admin_page(request):
#     return render(request, "members/admin_users.html")