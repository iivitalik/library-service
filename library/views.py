from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from library.models import Book, Borrowing
from library.serializers import BookSerializer, BorrowingSerializer, PaymentSerializer


class BookViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = BookSerializer
    queryset = Book.objects.all()


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = PaymentSerializer
    fields = "__all__"