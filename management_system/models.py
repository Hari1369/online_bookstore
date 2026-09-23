from django.db import models
from django.contrib.auth.models import User


class ProductBookCategory(models.Model):
    choice = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "product_category"

    def __str__(self):
        return self.choice


class ProductBookDetails(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ProductBookCategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    publication_year = models.IntegerField()
    image = models.ImageField(upload_to="images/books/", null=True,blank=True)
    pdf = models.FileField(upload_to="books/pdf/", null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_details"

    def __str__(self):
        return f"{self.isbn} - {self.title}"


class CartManagement(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart"

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(CartManagement, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductBookDetails, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cart_item"
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["cart", "product"],
        #         name="unique_cart_product"
        #     )
        # ]

    def __str__(self):
        return f"{self.cart.user.username} - {self.product.title}"


class Order(models.Model):
    STATUS_CHOICES = [("PENDING", "Pending"), ("SHIPPED", "Shipped"), ("DELIVERED", "Delivered"), ("CANCELLED", "Cancelled")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=30,unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"{self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductBookDetails, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_item"

    def __str__(self):
        return f"{self.order.order_number} - {self.product.title}"