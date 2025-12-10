from rest_framework import serializers

from library.models import Book, Borrowing, Payment


class BookSerializer(serializers.ModelSerializer):
    model = Book
    fields = "__all__"


class BorrowingSerializer(serializers.ModelSerializer):
    model = Borrowing
    fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    model = Payment
    fields = "__all__"