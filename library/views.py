from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from library.models import Book, Borrowing
from library.serializers import BookSerializer, BorrowingSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.all()

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            if is_active_bool:
                queryset = queryset.filter(actual_return_date__isnull=True)
            else:
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    def create(self, request):
        book_id = request.data.get('book_id')
        days = request.data.get('days', 14)

        if not book_id:
            return Response(
                {'error': 'book_id is required'},
                status=400
            )

        try:
            book = Book.objects.get(id=book_id)
            borrowing = book.borrow(request.user, days)
            return Response(
                BorrowingSerializer(borrowing).data,
                status=status.HTTP_201_CREATED
            )
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=400
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=400
            )

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        try:
            borrowing.return_book()
            return Response(
                BorrowingSerializer(borrowing).data,
                status=200
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=400
            )


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
