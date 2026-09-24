from django.db.models import Sum

from .models import CartItem


def cart_count(request):
    """Adds `cart_count` (total quantity in the user's cart) to every template."""
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        n = CartItem.objects.filter(cart__user=user).aggregate(n=Sum("quantity"))["n"]
        return {"cart_count": n or 0}
    return {"cart_count": 0}
