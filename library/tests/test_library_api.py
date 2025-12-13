from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Borrowing

User = get_user_model()


class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=5,
            daily_fee=1.50
        )

    def test_get_books(self):
        response = self.client.get("/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Book")

    def test_create_book(self):
        data = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 3,
            "daily_fee": "2.00"
        }
        response = self.client.post("/books/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(response.data["title"], "New Book")


class BorrowingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=3,
            daily_fee=1.50
        )

    def test_create_borrowing(self):
        initial_inventory = self.book.inventory
        data = {"book": self.book.id}

        response = self.client.post("/borrowings/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory - 1)

    def test_create_borrowing_unavailable(self):
        self.book.inventory = 0
        self.book.save()

        data = {"book": self.book.id}
        response = self.client.post("/borrowings/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unavailable", response.data["error"].lower())


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=5,
            daily_fee=2.00
        )

    def test_is_available_property(self):
        self.assertTrue(self.book.is_available)

        self.book.inventory = 0
        self.assertFalse(self.book.is_available)


class BorrowingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            inventory=5
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user
        )

    def test_borrowing_creation(self):
        expected_date = timezone.now().date() + timedelta(days=14)
        self.assertEqual(self.borrowing.expected_return_date, expected_date)

    def test_is_active_property(self):
        self.assertTrue(self.borrowing.is_active)
        self.borrowing.actual_return_date = timezone.now().date()
        self.assertFalse(self.borrowing.is_active)
