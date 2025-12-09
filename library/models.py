from django.utils import timezone

from django.core.validators import MinValueValidator
from django.db import models

from user.models import User


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    inventory = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    daily_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    cover = models.CharField(
        max_length=10,
        choices=CoverChoices.choices,
        default=CoverChoices.HARD,
    )

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    actual_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.book} return by {self.expected_return_date}"


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeChoices(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        max_length=10,
        default=StatusChoices.PENDING,
        choices=StatusChoices.choices
    )
    type = models.CharField(
        max_length=10,
        default=TypeChoices.PAYMENT,
        choices=TypeChoices.choices
    )
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=555)
    session_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.status} {self.type}"

    def calculate_money_to_pay(self) -> float:
        borrowing = self.borrowing

        if self.type == self.TypeChoices.PAYMENT:
            days = (borrowing.expected_return_date - borrowing.borrow_date).days
            days = days if days >= 1 else 1
            return float(days * borrowing.book.daily_fee)

        elif self.type == self.TypeChoices.FINE:
            if borrowing.actual_return_date:
                overdue_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
            else:
                from django.utils import timezone
                overdue_days = (timezone.now().date() - borrowing.expected_return_date).days

            if overdue_days <= 0:
                return 0.0

            return float(overdue_days * borrowing.book.daily_fee * 2)

        return 0.0



