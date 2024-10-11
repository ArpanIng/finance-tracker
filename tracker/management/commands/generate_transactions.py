import random

from django.core.management.base import BaseCommand
from faker import Faker

from tracker.models import Category, Transaction, TransactionTextChoices, User


class Command(BaseCommand):
    help = "Create dummy transactions"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # get the user
        user = User.objects.filter(username="admin").first()
        if not user:
            user = User.objects.create_superuser(
                username="admin", password="superadmin"
            )

        category_list = [
            "Bills",
            "Food",
            "Clothes",
            "Medicine",
            "Housing",
            "Salary",
            "Social",
            "Transport",
            "Vacation",
        ]
        for category_name in category_list:
            category_type = (
                TransactionTextChoices.INCOME
                if category_name == "Salary"
                else TransactionTextChoices.EXPENSE
            )
            category, created = Category.objects.get_or_create(
                name=category_name, user=user, type=category_type
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"{len(category_list)} categories created.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Category '{category_name}' already exists.")
                )

        categories = Category.objects.all()
        transaction_type_choices = [
            TransactionTextChoices.INCOME,
            TransactionTextChoices.EXPENSE,
        ]
        for i in range(5):
            transaction_type = random.choice(transaction_type_choices)
            # TODO: use bulk_create()
            Transaction.objects.create(
                note=fake.word(),
                category=random.choice(categories),
                user=user,
                type=transaction_type,
                amount=random.uniform(10, 2000),
                date=fake.date_between(start_date="-1y", end_date="today"),
            )
        self.stdout.write(self.style.SUCCESS("Transactions created successfully."))
