from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),
    path("show_users/", views.show_users, name="show_users"),
    path("update_user/<int:user_id>/", views.update_user, name="update_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),


    # ---------------------------------------------------------------- Forgot password
    # 1. User enters their email -> we email a one-time reset link.
    path(
        "forgot_password/",
        auth_views.PasswordResetView.as_view(
            template_name="members/forgot_password.html",
            email_template_name="members/password_reset_email.html",
            subject_template_name="members/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
            extra_email_context={"timeout_minutes": settings.PASSWORD_RESET_TIMEOUT // 60},
        ),
        name="password_reset",
    ),
    # 2. "Check your email" page (same message whether or not the email exists).
    path(
        "forgot_password/sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="members/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    # 3. The link from the email: <uid>/<token>. Shows the "new password" form.
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="members/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    # 4. Success page.
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="members/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]