from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

User = get_user_model()

from tracker.choices import TransactionTextChoices
from tracker.models import Category, Transaction


class CategoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="john", password="lorempass")
        cls.category = Category.objects.create(
            name="Sports", user=cls.user, type=TransactionTextChoices.INCOME
        )

    def test_verbose_name_meta_option(self):
        verbose_name = Category._meta.verbose_name
        verbose_name_plural = Category._meta.verbose_name_plural
        self.assertEqual(verbose_name, "Category")
        self.assertEqual(verbose_name_plural, "Categories")

    def test_unique_user_category_per_type_constraint(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name="Sports", user=self.user, type=TransactionTextChoices.INCOME
            )

    def test_model_str(self):
        self.assertEqual(str(self.category), "Sports")


class TransactionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="john", email="john@example.com", password="lorempass"
        )
        cls.category = Category.objects.create(
            name="Sports", user=cls.user, type=TransactionTextChoices.INCOME
        )
        cls.transaction = Transaction.objects.create(
            note="Maintain transaction",
            category=cls.category,
            user=cls.user,
            type=TransactionTextChoices.INCOME,
            amount=Decimal("100.00"),
            date=timezone.now(),
        )

    def test_negative_transaction_amount_constraint(self):
        self.transaction.amount = Decimal("-10.00")
        with self.assertRaises(IntegrityError):
            self.transaction.save()

    def test_negative_transaction_amount(self):
        self.transaction.amount = Decimal("-10.00")
        with self.assertRaises(ValidationError) as context:
            self.transaction.clean()

        amount_exception = context.exception
        self.assertIn("amount", amount_exception.message_dict)
        self.assertEqual(
            amount_exception.message_dict["amount"], ["Amount cannot be negative."]
        )

    def test_ordering_meta_option(self):
        ordering = Transaction._meta.ordering
        self.assertEqual(ordering, ["-date"])

    def test_string_representation_method(self):
        self.assertEqual(str(self.transaction), "Maintain transaction")
