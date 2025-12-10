from django.urls import path, include
from rest_framework import routers

from library.views import BorrowingViewSet, BookViewSet

app_name = "library"
router = routers.DefaultRouter()

router.register("borrowing", BorrowingViewSet)
router.register("books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
