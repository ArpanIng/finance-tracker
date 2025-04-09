from django.db import models
from django.db.models import FloatField, Q, Sum
from django.db.models.functions import TruncMonth

from .choices import TransactionTextChoices


class TransactionQuerySet(models.QuerySet):
    def get_income(self):
        return self.filter(type=TransactionTextChoices.INCOME)

    def get_expense(self):
        return self.filter(type=TransactionTextChoices.EXPENSE)

    def get_total_income_and_expense(self):
        """Returns total sum of incomes and expenses"""
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

    def get_net_income(self):
        totals = self.get_total_income_and_expense()
        total_incomes = totals["total_income"]
        total_expense = totals["total_expense"]
        net_income = total_incomes - total_expense
        return net_income

    def total_balance(self):
        """Returns total sum of transactions balance."""

        return self.aggregate(
            total=Sum("amount", output_field=FloatField(), default=0)
        )["total"]

    def get_monthly_totals(self):
        """
        Returns total sum of incomes and expenses per month
        """

        return (
            self.annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
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
        )
