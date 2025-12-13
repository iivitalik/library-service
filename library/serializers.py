from rest_framework import serializers
from library.models import Book, Borrowing


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'inventory',
            'daily_fee', 'cover', 'is_available'
        ]
        read_only_fields = ['id', 'is_available']


class BorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    daily_fee = serializers.DecimalField(
        source='book.daily_fee',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            'id', 'book', 'book_title', 'user', 'user_email',
            'borrow_date', 'expected_return_date', 'actual_return_date',
            'daily_fee', 'is_active', 'is_overdue'
        ]
        read_only_fields = [
            'id', 'borrow_date', 'daily_fee', 'is_active', 'is_overdue'
        ]