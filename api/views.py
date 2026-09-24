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
)
from management_system.models import (
    ProductBookDetails,
    ProductBookCategory,
)
from .serializers import (
    SignupSerializer,
    UserSerializer,
    BookSerializer,
)




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


class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        if request.auth:
            request.auth.delete()
        return Response({
            "message": "Logout successful."
        })

class MeAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(
            UserSerializer(request.user).data
        )


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



# {
#     "message": "Login successful.",
#     "token": "ff05b3e67fd182f79b2d5b3b2a11e28b7f80299e",
#     "user": {
#         "id": 1,
#         "username": "test",
#         "first_name": "test",
#         "last_name": "dummy",
#         "email": "test@gmail.com",
#         "is_staff": True,
#         "is_active": True
#     }
# }