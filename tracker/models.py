from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .choices import TransactionTextChoices
from .managers import TransactionQuerySet


class Category(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
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


class Transaction(models.Model):
    note = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, null=True, blank=True, default="")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    type = models.CharField(max_length=3, choices=TransactionTextChoices.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TransactionQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name="amount_gt_0",
                violation_error_message="Amount cannot be negative.",
            )
        ]
        ordering = ["-date"]

    def __str__(self):
        return self.note

    def clean(self):
        if self.amount and self.amount < 0:
            raise ValidationError({"amount": "Amount cannot be negative."})
