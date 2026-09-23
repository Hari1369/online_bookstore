from django.urls import path
from . import views

urlpatterns = [
    path("admin_page/", views.admin_page, name="admin_view"),
    path("signup/", views.signup_page, name="signup"),
    path("login/", views.login_page, name="login"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
]