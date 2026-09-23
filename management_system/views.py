from django.shortcuts import render

# Create your views here.
def cart_page(request):
    return render(request, "management_system/cart.html")

def index_page(request):
    return render(request, "management_system/index.html")

def orders_page(request):
    return render(request, "management_system/orders.html")

def product_page(request):
    return render(request, "management_system/product.html")