from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator
from rest_framework.exceptions import ValidationError
from user.models import User


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    inventory = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(0)]
    )
    daily_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        validators=[MinValueValidator(0.01)]
    )
    cover = models.CharField(
        max_length=4,
        choices=CoverChoices.choices,
        default=CoverChoices.HARD,
    )

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.inventory > 0


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowings")

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"{self.book.title} return by {self.expected_return_date}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expected_return_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.actual_return_date is None

    def is_overdue(self):
        if self.actual_return_date:
            return self.actual_return_date > self.expected_return_date
        return timezone.now().date() > self.expected_return_date

    def return_book(self):
        if not self.is_active:
            raise ValidationError("Book already returned")

        self.actual_return_date = timezone.now().date()
        self.save()

        self.book.inventory += 1
        self.book.save()

        Payment.objects.create(
            borrowing=self,
            type=Payment.TypeChoices.PAYMENT
        )

        if self.is_overdue():
            Payment.objects.create(
                borrowing=self,
                type=Payment.TypeChoices.FINE
            )


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
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    session_url = models.URLField(max_length=555, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.status} {self.type}"

    def save(self, *args, **kwargs):
        if not self.money_to_pay or self.money_to_pay == 0:
            self.money_to_pay = self.calculate_money_to_pay()
        super().save(*args, **kwargs)

    def calculate_money_to_pay(self) -> float:
        if self.type == self.TypeChoices.PAYMENT:
            days = (self.borrowing.expected_return_date - self.borrowing.borrow_date).days
            days = max(days, 1)
            return float(days * self.borrowing.book.daily_fee)

        elif self.type == self.TypeChoices.FINE:
            if self.borrowing.actual_return_date:
                overdue_days = (self.borrowing.actual_return_date - self.borrowing.expected_return_date).days
            else:
                overdue_days = (timezone.now().date() - self.borrowing.expected_return_date).days

            if overdue_days <= 0:
                return 0.0

            return float(overdue_days * self.borrowing.book.daily_fee * 2)

        return 0.0
