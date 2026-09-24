from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .decorators import admin_required, admin_api_required
import json


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


@require_http_methods(["PUT"])
@admin_api_required
def update_user(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in."}, status=401)
    if not request.user.is_staff:
        return JsonResponse({"error": "You do not have permission to edit users."}, status=403)
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
 
    required = ["first_name", "last_name", "email", "is_staff", "is_active"]
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({"error": "Missing fields: " + ", ".join(missing)}, status=400)
 
    first_name = str(data["first_name"]).strip()
    last_name = str(data["last_name"]).strip()
    email = str(data["email"]).strip()
    is_staff = data["is_staff"]
    is_active = data["is_active"]
 
    if not isinstance(is_staff, bool) or not isinstance(is_active, bool):
        return JsonResponse({"error": "is_staff and is_active must be true or false."}, status=400)
    if len(first_name) > 150 or len(last_name) > 150:
        return JsonResponse({"error": "Names must be 150 characters or fewer."}, status=400)
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "Enter a valid email address."}, status=400)
    if User.objects.filter(email__iexact=email).exclude(pk=target.pk).exists():
        return JsonResponse({"error": "This email is already registered."}, status=400)
    if target.pk == request.user.pk and (not is_staff or not is_active):
        return JsonResponse(
            {"error": "You cannot remove your own staff access or deactivate yourself."},
            status=400,
        )
    if not request.user.is_superuser:
        if target.is_superuser:
            return JsonResponse({"error": "Only a superuser can edit a superuser."}, status=403)
        if is_staff != target.is_staff:
            return JsonResponse({"error": "Only a superuser can change staff status."}, status=403)


    target.first_name = first_name
    target.last_name = last_name
    target.email = email
    target.is_staff = is_staff
    target.is_active = is_active
    target.save()
 
    return JsonResponse({
        "message": "User updated.",
        "user": {
            "id": target.pk,
            "first_name": target.first_name,
            "last_name": target.last_name,
            "email": target.email,
            "is_staff": target.is_staff,
            "is_active": target.is_active,
        },
    })
 
 
@require_http_methods(["DELETE"])
@admin_api_required
def delete_user(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in."}, status=401)
    if not request.user.is_staff:
        return JsonResponse({"error": "You do not have permission to delete users."}, status=403)
 
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
 
    if target.pk == request.user.pk:
        return JsonResponse({"error": "You cannot delete your own account."}, status=400)
    if target.is_superuser and not request.user.is_superuser:
        return JsonResponse({"error": "Only a superuser can delete a superuser."}, status=403)
    if not target.is_active:
        return JsonResponse({"error": "This user is already inactive."}, status=400)
 
    target.is_active = False
    target.save(update_fields=["is_active"])
 
    return JsonResponse({
        "message": "User deactivated.",
        "user": {
            "id": target.pk,
            "first_name": target.first_name,
            "last_name": target.last_name,
            "email": target.email,
            "is_staff": target.is_staff,
            "is_active": target.is_active,
        },
    })


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

def logout_page(request):
    logout(request)
    return redirect("login")

def show_users(request):
    user_data = User.objects.all()
    return render(request, "members/users_data.html", {"users": user_data})


def forgot_password(request):
    return render(request, "members/forgot_password.html")


# def admin_page(request):
#     return render(request, "members/admin_users.html")