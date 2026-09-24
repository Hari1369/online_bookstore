from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("show_users/", views.show_users, name="show_users"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),

]