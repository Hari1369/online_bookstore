from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction

from management_system.models import (
    ProductBookDetails,
    ProductBookCategory,
    CartItem,
    CartManagement,
)

from .serializers import (
    SignupSerializer,
    UserSerializer,
    BookSerializer,
)



# =========================================================>
# =========================================================>
# ==========================================>  SIGN UP PAGE 
# =========================================================>
# =========================================================>
class SignupAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "message": "Account created successfully.",
                    "token": token.key,
                    "user": UserSerializer(user).data,
                },
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


# =========================================================>
# =========================================================>
# =========================================>  LOGIN UP PAGE 
# =========================================================>
# =========================================================>

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {
                    "error": "Username and password are required."
                },
                status=400
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "error": "Invalid username or password."
                },
                status=401
            )

        token, created = Token.objects.get_or_create(
            user=user
        )

        return Response({
            "message": "Login successful.",
            "token": token.key,
            "user": UserSerializer(user).data,
        })


# =========================================================>
# =========================================================>
# ==========================================>  LOGOUT PAGE 
# =========================================================>
# =========================================================>

class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.auth:
            request.auth.delete()
        return Response({
            "message": "Logout successful."
        })

# =========================================================>
# =========================================================>
# ==========================================>  MEAPI PAGE 
# =========================================================>
# =========================================================>

class MeAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            UserSerializer(request.user).data
        )



# =========================================================>
# =========================================================>
# ==========================================>  BOOKCREATE PAGE 
# =========================================================>
# =========================================================>

class BookListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        books = ProductBookDetails.objects.select_related(
            "category"
        ).filter(
            is_active=True
        ).order_by("-id")

        serializer = BookSerializer(
            books,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Only admin can create books."
                },
                status=403
            )
        serializer = BookSerializer(
            data=request.data
        )
        if serializer.is_valid():
            book = serializer.save()
            return Response(
                BookSerializer(book).data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )


# =========================================================>
# =========================================================>
# ==========================================>  BOOKLIST PAGE 
# =========================================================>
# =========================================================>

class BookDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self, book_id):
        return get_object_or_404(
            ProductBookDetails,
            id=book_id
        )

    def get(self, request, book_id):
        book = self.get_object(book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, book_id):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Only admin can update books."
                },
                status=403
            )

        book = self.get_object(book_id)
        serializer = BookSerializer(
            book,
            data=request.data
        )

        if serializer.is_valid():
            book = serializer.save()
            return Response(
                BookSerializer(book).data
            )
        return Response(
            serializer.errors,
            status=400
        )

    def delete(self, request, book_id):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Only admin can delete books."
                },
                status=403
            )

        book = self.get_object(book_id)
        book.is_active = False
        book.save(
            update_fields=["is_active"]
        )
        return Response({
            "message": "Book deactivated successfully."
        })

# =========================================================>
# =========================================================>
# ==========================================>  BOOKLIST PAGE 
# =========================================================>
# =========================================================>

class CartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart, created = CartManagement.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)
        if not product_id:
            return Response(
                {
                    "error": "Product is required."
                },
                status=400
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):

            return Response(
                {
                    "error": "Quantity must be a number."
                },
                status=400
            )
        if quantity < 1:
            return Response(
                {
                    "error": "Quantity must be at least 1."
                },
                status=400
            )

        try:
            product = ProductBookDetails.objects.get(
                id=product_id,
                is_active=True
            )

        except ProductBookDetails.DoesNotExist:
            return Response(
                {
                    "error": "Book not found."
                },
                status=404
            )
        if quantity > product.available_copies:
            return Response(
                {
                    "error":
                        f"Only {product.available_copies} copies available."
                },
                status=400
            )

        cart, created = CartManagement.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart,product=product,
            defaults={
                "quantity": quantity
            })

        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > product.available_copies:
                return Response(
                    {
                        "error":
                            f"Only {product.available_copies} copies available."
                    },
                    status=400
                )

            item.quantity = new_quantity
            item.save()

        return Response(
            CartSerializer(cart).data,
            status=201
        )

# =========================================================>
# =========================================================>
# ==========================================>  CARTITEM PAGE 
# =========================================================>
# =========================================================>

class CartItemAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, request, item_id):
        return get_object_or_404(
            CartItem,
            id=item_id,
            cart__user=request.user
        )
    def put(self, request, item_id):
        item = self.get_object(
            request,
            item_id
        )
        quantity = request.data.get("quantity")
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Quantity must be a number."
                },
                status=400
            )
        if quantity < 1:
            return Response(
                {
                    "error": "Quantity must be at least 1."
                },
                status=400
            )
        if quantity > item.product.available_copies:
            return Response(
                {
                    "error":
                        f"Only {item.product.available_copies} copies available."
                },
                status=400
            )
        item.quantity = quantity
        item.save()
        cart = item.cart
        return Response(
            CartSerializer(cart).data
        )
    def delete(self, request, item_id):
        item = self.get_object(
            request,
            item_id
        )
        cart = item.cart
        item.delete()
        return Response(
            CartSerializer(cart).data
        )






# =========================================================>
# =========================================================>
# ================================>  ORDERLISTCREATEAPI PAGE 
# =========================================================>
# =========================================================>

class OrderListCreateAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related(
            "orderitem_set__product"
        ).order_by("-id")
        serializer = OrderSerializer(
            orders,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        with transaction.atomic():
            cart = CartManagement.objects.filter(
                user=request.user
            ).first()
            if not cart:
                return Response(
                    {
                        "error": "Your cart is empty."
                    },
                    status=400
                )
            cart_items = list(
                CartItem.objects.filter(
                    cart=cart
                )
            )
            if not cart_items:
                return Response(
                    {
                        "error": "Your cart is empty."
                    },
                    status=400
                )
            total = Decimal("0.00")
            for item in cart_items:
                product = ProductBookDetails.objects.select_for_update().get(
                    id=item.product_id
                )
                if not product.is_active:
                    return Response(
                        {
                            "error":
                                f"{product.title} is not available."
                        },
                        status=400
                    )
                if item.quantity > product.available_copies:
                    return Response(
                        {
                            "error":
                                f"Only {product.available_copies} copies "
                                f"of {product.title} are available."
                        },
                        status=400
                    )
                total += (product.price * item.quantity)
            order_number = ("ORD-" + timezone.now().strftime("%Y%m%d") + "-" + uuid.uuid4().hex[:6].upper())
            order = Order.objects.create(
                user=request.user,
                order_number=order_number,
                total_amount=total,
            )
            for item in cart_items:
                product = ProductBookDetails.objects.select_for_update().get(
                    id=item.product_id
                )
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )
                product.available_copies -= item.quantity
                product.save(
                    update_fields=[
                        "available_copies",
                        "updated_at"
                    ]
                )
            CartItem.objects.filter(
                cart=cart
            ).delete()
        return Response(
            OrderSerializer(order).data,
            status=201
        )




# =========================================================>
# =========================================================>
# ==========================================>  CARTITEM PAGE 
# =========================================================>
# =========================================================>

class OrderDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, request, order_id):
        if request.user.is_superuser:
            return get_object_or_404(
                Order,
                id=order_id
            )
        return get_object_or_404(Order, id=order_id, user=request.user)

    def get(self, request, order_id):
        order = self.get_object(request, order_id)
        return Response(OrderSerializer(order).data)

    def put(self, request, order_id):
        if not request.user.is_superuser:
            return Response(
                {
                    "error":"Only admin can update order status."
                },
                status=403
            )

        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get("status")

        valid_statuses = ["PENDING", "SHIPPED", "DELIVERED", "CANCELLED"]

        if new_status not in valid_statuses:
            return Response(
                {
                    "error":"Invalid status.",
                    "valid_statuses":valid_statuses
                },
                status=400
            )

        order.status = new_status
        order.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        return Response(
            OrderSerializer(order).data
        )

    def delete(self, request, order_id):
        if not request.user.is_superuser:
            return Response(
                {
                    "error": "Only admin can delete orders."
                },
                status=403
            )

        order = get_object_or_404(Order, id=order_id)

        order.delete()
        return Response({
            "message": "Order deleted successfully."
        })





# {
#     "message": "Login successful.",
#     "token": "c23246afe16f82b573c6baee4746da627849ec05",
#     "user": {
#         "id": 5,
#         "username": "hari",
#         "first_name": "Hari",
#         "last_name": "Mondal",
#         "email": "hari@gmail.com",
#         "is_staff": false,
#         "is_active": true
#     }
# }