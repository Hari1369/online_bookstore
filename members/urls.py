from django.urls import path
from . import views

urlpatterns = [
    path("show_users/", views.show_users, name="show_users"),
    path("signup/", views.signup_page, name="signup"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_page, name="logout"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
]