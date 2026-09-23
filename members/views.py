from django.shortcuts import render

# Create your views here.
def signup_page(request):
    return render(request, "members/signup.html")


def login_page(request):
    return render(request, "members/login.html")


def forgot_password(request):
    return render(request, "members/forgot_password.html")


def admin_page(request):
    return render(request, "members/admin_users.html")