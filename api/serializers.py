from django.contrib.auth.models import User
from rest_framework import serializers
from management_system.models import (
    ProductBookCategory,
    ProductBookDetails,
    CartManagement,
    CartItem,
    Order,
    OrderItem,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
        ]


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        user.is_staff = False
        user.is_superuser = False
        user.is_active = True

        user.save()

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBookCategory
        fields = [
            "id",
            "choice",
        ]


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.choice",
        read_only=True
    )
    class Meta:
        model = ProductBookDetails
        fields = [
            "id",
            "isbn",
            "title",
            "author",
            "description",
            "category",
            "category_name",
            "price",
            "publication_year",
            "image",
            "pdf",
            "total_copies",
            "available_copies",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        total_copies = data.get(
            "total_copies",
            getattr(self.instance, "total_copies", 0)
        )

        available_copies = data.get(
            "available_copies",
            getattr(self.instance, "available_copies", 0)
        )
        if available_copies > total_copies:
            raise serializers.ValidationError({
                "available_copies":
                    "Available copies cannot exceed total copies!"
            })

        return data


class CartItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(
        source="product",
        read_only=True
    )
    subtotal = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "book",
            "quantity",
            "subtotal",
        ]

    def get_subtotal(self, obj):

        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    class Meta:
        model = CartManagement
        fields = [
            "id",
            "user",
            "items",
            "total",
        ]

    def get_items(self, obj):
        items = CartItem.objects.filter(
            cart=obj
        ).select_related("product")
        return CartItemSerializer(
            items,
            many=True
        ).data
    def get_total(self, obj):
        total = 0
        items = CartItem.objects.filter(cart=obj).select_related("product")
        for item in items:
            total = total + item.product.price * item.quantity

        return total


class OrderItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(
        source="product.title",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "book_title",
            "quantity",
            "price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
            "items",
        ]

    def get_items(self, obj):

        items = OrderItem.objects.filter(
            order=obj
        ).select_related("product")

        return OrderItemSerializer(
            items,
            many=True
        ).data