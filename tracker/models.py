from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import FloatField, Q, Sum


class User(AbstractUser):
    pass


class TransactionTextChoices(models.TextChoices):
    INCOME = "INC", "Income"
    EXPENSE = "EXP", "Expense"


class Category(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TransactionTextChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user", "type"], name="unique_user_category_per_type"
            )
        ]

    def __str__(self):
        return self.name


class TransactionQuerySet(models.QuerySet):
    def get_income(self):
        return self.filter(type=TransactionTextChoices.INCOME)

    def get_expense(self):
        return self.filter(type=TransactionTextChoices.EXPENSE)

    def get_total_income_and_expense(self):
        totals = self.aggregate(
            total_income=Sum(
                "amount",
                filter=Q(type=TransactionTextChoices.INCOME),
                output_field=FloatField(),
                default=0,
            ),
            total_expense=Sum(
                "amount",
                filter=Q(type=TransactionTextChoices.EXPENSE),
                output_field=FloatField(),
                default=0,
            ),
        )
        return totals

    def total_balance(self, user):
        """Calculate the total balance of transactions for a request user."""

        return self.filter(user=user).aggregate(
            total=Sum("amount", output_field=FloatField(), default=0)
        )["total"]


class Transaction(models.Model):
    note = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, null=True, blank=True, default="")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TransactionTextChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.note
