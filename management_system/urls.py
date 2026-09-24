from django.urls import path
from . import views

urlpatterns = [
    path("index_page/", views.index_page, name="main"),
    path("cart_page/", views.cart_page, name="cart"),
    path("orders_page/", views.orders_page, name="orders"),
    path("product_page/", views.product_page, name="product"),
    path("product_category/", views.product_category_page, name="product_category"),
    path("update_category/<int:category_id>/", views.update_category, name="update_category"),
    path("product_update_page/", views.product_update_page, name="product_update_page"),
    path('manage_books/update/<int:product_id>/', views.product_update, name='product_update'),
    path('manage_books/delete/<int:product_id>/', views.product_delete, name='product_delete'),

    path("cart_page/", views.cart_page, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
 
    path("orders_page/", views.orders_page, name="orders"),
    path("orders/place/", views.order_place, name="order_place"),
    path("orders/update/<int:order_id>/", views.order_update, name="order_update"),
    path("orders/delete/<int:order_id>/", views.order_delete, name="order_delete"),
]