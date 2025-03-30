from django.db import models


class TransactionTextChoices(models.TextChoices):
    INCOME = "INC", "Income"
    EXPENSE = "EXP", "Expense"
