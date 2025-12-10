from rest_framework import serializers

from library.models import Book, Borrowing


class BookSerializer(serializers.ModelSerializer):
    model = Book
    fields = "__all__"


class BorrowingSerializer(serializers.ModelSerializer):
    model = Borrowing
    fields = "__all__"


