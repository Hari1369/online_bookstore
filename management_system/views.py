from django.shortcuts import render, redirect
from .models import ProductBookCategory, ProductBookDetails, CartManagement, CartItem, Order, OrderItem
from .forms import (ProductBookCategoryForm, BookCategoryCSVForm, ProductBookDetailsForm) 
from django.contrib import messages
from django.http import JsonResponse
import csv
import json



def index_page(request):
    # Query all active books and prefetch foreign key relations for optimal database calls
    books = ProductBookDetails.objects.filter(is_active=True).select_related('category')
    categories = ProductBookCategory.objects.all()

    context = {
        'books': books,
        'categories': categories,
    }
    return render(request, "management_system/index.html", context)



def cart_page(request):
    return render(request, "management_system/cart.html")

def orders_page(request):
    return render(request, "management_system/orders.html")

def product_page(request):
    if request.method == "POST":
        form = ProductBookDetailsForm(
            request.POST,
            request.FILES
        )
        if form.is_valid():
            form.save()
            return redirect("product")
    else:
        form = ProductBookDetailsForm()
    return render(request,"management_system/product.html",{"form": form})


def product_category_page(request):
    category_form = ProductBookCategoryForm()
    csv_form = BookCategoryCSVForm()
    if request.method == "POST":
        if "add_category" in request.POST:
            category_form = ProductBookCategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                return redirect("product_category")
        elif "upload_csv" in request.POST:
            csv_form = BookCategoryCSVForm(
                request.POST,
                request.FILES
            )
            if csv_form.is_valid():
                csv_file = csv_form.cleaned_data["csv_file"]
                decoded_file = (
                    csv_file
                    .read()
                    .decode("utf-8")
                    .splitlines()
                )

                reader = csv.DictReader(decoded_file)
                existing_categories = []
                added_categories = []
                for row in reader:
                    category = row["Book_Category"].strip()
                    if category:
                        if ProductBookCategory.objects.filter(
                            choice=category
                        ).exists():

                            existing_categories.append(category)

                        else:
                            ProductBookCategory.objects.create(
                                choice=category
                            )
                            added_categories.append(category)


                if len(existing_categories) > 3:
                    messages.warning(
                        request,
                        "Many categories already exist in the system!"
                    )
                elif existing_categories:
                    messages.warning(
                        request,
                        "Already existing categories: "
                        + ", ".join(existing_categories)
                    )
                if added_categories:
                    messages.success(request, "Categories added successfully: " + ", ".join(added_categories))
                return redirect("product_category")

    categories = ProductBookCategory.objects.all().order_by("id")
    return render(
        request,
        "management_system/product_category.html",
        {
            "form": category_form,
            "csv_form": csv_form,
            "categories": categories,
        }
    )



def update_category(request, category_id):
    if request.method == "PUT":
        category = ProductBookCategory.objects.get(id=category_id)
        data = json.loads(request.body)
        new_name = data.get("choice", "").strip()

        if not new_name:
            return JsonResponse({"error": "Category name cannot be empty!"}, status=400)

        if ProductBookCategory.objects.filter(choice=new_name).exclude(id=category_id).exists():
            return JsonResponse({
                "error": "This category already exists."
            }, status=400)

        category.choice = new_name
        category.save()

        return JsonResponse({
            "message": "Category updated successfully!",
            "id": category.id,
            "choice": category.choice
        })