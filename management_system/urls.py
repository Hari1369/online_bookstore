from django.urls import path
from . import views

urlpatterns = [
    path("index_page/", views.index_page, name="main"),
    path("cart_page/", views.cart_page, name="cart"),
    path("orders_page/", views.orders_page, name="orders"),
    path("product_page/", views.product_page, name="product"),
]