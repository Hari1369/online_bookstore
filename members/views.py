from django.shortcuts import render, redirect
from .forms import SignupForm



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
    return render(request, "members/login.html")


def forgot_password(request):
    return render(request, "members/forgot_password.html")


def admin_page(request):
    
    return render(request, "members/admin_users.html")