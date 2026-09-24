from django.urls import path

from .views import (
    SignupAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    BookListCreateAPIView,
    BookDetailAPIView,
)


urlpatterns = [

    # =========================
    # AUTH APIs
    # =========================

    path(
        "auth/signup/",
        SignupAPIView.as_view(),
        name="api_signup"
    ),

    path(
        "auth/login/",
        LoginAPIView.as_view(),
        name="api_login"
    ),

    path(
        "auth/logout/",
        LogoutAPIView.as_view(),
        name="api_logout"
    ),

    path(
        "auth/me/",
        MeAPIView.as_view(),
        name="api_me"
    ),


    # =========================
    # BOOK APIs
    # =========================

    path(
        "books/",
        BookListCreateAPIView.as_view(),
        name="api_books"
    ),

    path(
        "books/<int:book_id>/",
        BookDetailAPIView.as_view(),
        name="api_book_detail"
    ),
]