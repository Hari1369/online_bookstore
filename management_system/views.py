from django.shortcuts import render, redirect

from django.contrib import messages
from django.http import JsonResponse
import csv
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import uuid
from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum
from django.http.request import RawPostDataException
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from members.decorators import admin_required, admin_api_required

from members.decorators import admin_api_required, login_required_api, login_required_page
from .models import CartItem, CartManagement, Order, OrderItem, ProductBookDetails, ProductBookCategory
from .forms import (ProductBookCategoryForm, BookCategoryCSVForm, ProductBookDetailsForm) 
from django.views.decorators.http import require_http_methods


def _json_body(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, RawPostDataException):
        return None
    return data if isinstance(data, dict) else None


def index_page(request):
    books = ProductBookDetails.objects.filter(is_active=True).select_related('category')
    categories = ProductBookCategory.objects.all()

    context = {'books': books, 'categories': categories}
    return render(request, "management_system/index.html", context)



# def cart_page(request):
#     return render(request, "management_system/cart.html")

# def orders_page(request):
#     return render(request, "management_system/orders.html")

@admin_required
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

@admin_required
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


@require_http_methods(["PUT"])
@admin_api_required
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


def _error(message, status=400):
    return JsonResponse({"error": message}, status=status)


def _copies(n):
    return f"{n} copy" if n == 1 else f"{n} copies"


def _money(value):
    return f"{Decimal(value):.2f}"


def _cart_count(user):
    return CartItem.objects.filter(cart__user=user).aggregate(n=Sum("quantity"))["n"] or 0


def _cart_total(user):
    total = Decimal("0.00")
    for item in CartItem.objects.filter(cart__user=user).select_related("product"):
        total += item.product.price * item.quantity
    return total

def _new_order_number():
    for _ in range(5):
        number = "ORD-{}-{}".format(timezone.now().strftime("%Y%m%d"), uuid.uuid4().hex[:6].upper())
        if not Order.objects.filter(order_number=number).exists():
            return number
    return "ORD-" + uuid.uuid4().hex[:16].upper()


def _restock(order):
    """Give the copies of every item in `order` back to the shelf."""
    for line in order.orderitem_set.all():
        ProductBookDetails.objects.filter(pk=line.product_id).update(
            available_copies=F("available_copies") + line.quantity
        )


# =================================================================== CART
@login_required_page
def cart_page(request):
    """VIEW: the user's cart with per-item subtotal and the total price."""
    items = (
        CartItem.objects.filter(cart__user=request.user)
        .select_related("product")
        .order_by("id")
    )
    rows = [{"item": it, "subtotal": it.product.price * it.quantity} for it in items]
    return render(request, "management_system/cart.html", {
        "rows": rows,
        "total": sum((r["subtotal"] for r in rows), Decimal("0.00")),
        "items_count": sum(r["item"].quantity for r in rows),
    })


@require_POST
@login_required_api
def cart_add(request, product_id):
    print("PRODUCT : ", product_id)

    body = _json_body(request) or {}
    try:
        qty = int(body.get("quantity", 1))
    except (TypeError, ValueError):
        return _error("Quantity must be a whole number.")
    if qty < 1:
        return _error("Quantity must be at least 1.")

    try:
        product = ProductBookDetails.objects.get(pk=product_id, is_active=True)
    except ProductBookDetails.DoesNotExist:
        return _error("This book is not available.", 404)

    with transaction.atomic():
        cart, _ = CartManagement.objects.get_or_create(user=request.user)
        existing = list(CartItem.objects.select_for_update().filter(cart=cart, product=product))
        in_cart = sum(i.quantity for i in existing)

        if in_cart + qty > product.available_copies:
            if product.available_copies == 0:
                return _error("Sorry, this book is out of stock.")
            note = f" (you already have {in_cart} in your cart)" if in_cart else ""
            return _error(f"Only {_copies(product.available_copies)} available{note}.")

        if existing:
            item = existing[0]
            item.quantity += qty
            item.save(update_fields=["quantity", "updated_at"])
        else:
            CartItem.objects.create(cart=cart, product=product, quantity=qty)

    return JsonResponse({
        "message": f"“{product.title}” added to your cart.",
        "cart_count": _cart_count(request.user),
    })


@require_http_methods(["PUT"])
@login_required_api
def cart_update(request, item_id):
    """UPDATE: change the quantity of one cart item (body: {"quantity": 3})."""
    try:
        item = CartItem.objects.select_related("product").get(pk=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        return _error("Cart item not found.", 404)

    body = _json_body(request)
    if body is None or "quantity" not in body:
        return _error("Send the new quantity as JSON, e.g. {\"quantity\": 2}.")
    try:
        qty = int(body["quantity"])
    except (TypeError, ValueError):
        return _error("Quantity must be a whole number.")
    if qty < 1:
        return _error("Quantity must be at least 1. Use Remove to delete the item.")

    product = item.product
    if not product.is_active:
        return _error("This book is no longer available. Please remove it from your cart.")
    if qty > product.available_copies:
        return _error(f"Only {_copies(product.available_copies)} available.")

    item.quantity = qty
    item.save(update_fields=["quantity", "updated_at"])

    return JsonResponse({
        "message": "Quantity updated.",
        "item": {"id": item.pk, "quantity": item.quantity, "subtotal": _money(product.price * qty)},
        "total": _money(_cart_total(request.user)),
        "cart_count": _cart_count(request.user),
    })


@require_http_methods(["DELETE"])
@login_required_api
def cart_remove(request, item_id):
    """DELETE: remove one item from the cart."""
    deleted, _ = CartItem.objects.filter(pk=item_id, cart__user=request.user).delete()
    if not deleted:
        return _error("Cart item not found.", 404)
    return JsonResponse({
        "message": "Item removed.",
        "total": _money(_cart_total(request.user)),
        "cart_count": _cart_count(request.user),
    })


# ================================================================= ORDERS
@require_POST
@login_required_api
def order_place(request):
    """CREATE: turn the cart into an order, reduce stock, empty the cart."""
    with transaction.atomic():
        cart = CartManagement.objects.filter(user=request.user).first()
        cart_items = list(CartItem.objects.filter(cart=cart)) if cart else []
        if not cart_items:
            return _error("Your cart is empty.")

        # merge duplicate rows of the same book, then lock those books
        wanted = defaultdict(int)
        for it in cart_items:
            wanted[it.product_id] += it.quantity
        products = {
            p.pk: p
            for p in ProductBookDetails.objects.select_for_update().filter(pk__in=wanted.keys())
        }

        problems = []
        for pid, qty in wanted.items():
            p = products[pid]
            if not p.is_active:
                problems.append(f"“{p.title}” is no longer available.")
            elif qty > p.available_copies:
                problems.append(f"Only {_copies(p.available_copies)} of “{p.title}” left.")
        if problems:
            return _error(" ".join(problems) + " Please update your cart.")

        total = sum((products[pid].price * qty for pid, qty in wanted.items()), Decimal("0.00"))
        order = Order.objects.create(
            user=request.user,
            order_number=_new_order_number(),
            total_amount=total,
        )
        for pid, qty in wanted.items():
            p = products[pid]
            OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price)  # price snapshot
            p.available_copies -= qty
            p.save(update_fields=["available_copies", "updated_at"])

        CartItem.objects.filter(cart=cart).delete()

    messages.success(request, f"Order {order.order_number} placed — thank you!")
    return JsonResponse({
        "message": "Order placed.",
        "order_number": order.order_number,
        "redirect": reverse("orders"),
    })


@login_required_page
def orders_page(request):
    """VIEW: customers see their own orders, admins see everybody's."""
    is_admin = request.user.is_superuser
    orders = (
        Order.objects.select_related("user")
        .prefetch_related("orderitem_set__product")
        .order_by("-created_at")
    )
    if not is_admin:
        orders = orders.filter(user=request.user)

    return render(request, "management_system/orders.html", {
        "orders": orders,
        "is_admin": is_admin,
        "statuses": Order.STATUS_CHOICES,
    })


@require_http_methods(["PUT"])
@admin_api_required
def order_update(request, order_id):
    """UPDATE (admin): change an order's status (body: {"status": "SHIPPED"})."""
    body = _json_body(request)
    new_status = str((body or {}).get("status", "")).upper()
    if new_status not in dict(Order.STATUS_CHOICES):
        return _error("Invalid status. Use: " + ", ".join(dict(Order.STATUS_CHOICES)) + ".")

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            return _error("Order not found.", 404)

        if order.status == "CANCELLED" and new_status != "CANCELLED":
            return _error("A cancelled order cannot be changed.")

        if new_status == "CANCELLED" and order.status != "CANCELLED":
            _restock(order)  # cancelled copies go back on the shelf

        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

    return JsonResponse({
        "message": "Order status updated.",
        "order": {"id": order.pk, "status": order.status, "status_display": order.get_status_display()},
    })


@require_http_methods(["DELETE"])
@admin_api_required
def order_delete(request, order_id):
    """DELETE (admin): permanently remove an order."""
    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            return _error("Order not found.", 404)

        # PENDING / SHIPPED orders still hold stock -> give it back.
        # CANCELLED were already restocked; DELIVERED copies have left the shop.
        if order.status in ("PENDING", "SHIPPED"):
            _restock(order)
        number = order.order_number
        order.delete()  # OrderItems are removed automatically (CASCADE)

    return JsonResponse({"message": f"Order {number} deleted."})
