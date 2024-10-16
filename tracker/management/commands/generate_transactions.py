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
            "Commissions",
            "Medicine",
            "Housing",
            "Salary",
            "Interest",
            "Social",
            "Transport",
            "Vacation",
        ]
        for category_name in category_list:
            category_type = (
                TransactionTextChoices.INCOME
                if category_name in ("Commissions", "Salary", "Interest")
                else TransactionTextChoices.EXPENSE
            )
            category, created = Category.objects.get_or_create(
                name=category_name, user=user, type=category_type
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"{category_name} category created.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Category '{category_name}' already exists.")
                )

        categories = Category.objects.all()
        income_categories = ["Salary", "Interest", "Commissions"]

        for i in range(50):
            category = random.choice(categories)
            if category.name in income_categories:
                transaction_type = TransactionTextChoices.INCOME
            else:
                transaction_type = TransactionTextChoices.EXPENSE
            # TODO: use bulk_create()
            Transaction.objects.create(
                note=fake.word(),
                category=category,
                user=user,
                type=transaction_type,
                amount=random.uniform(10, 2000),
                date=fake.date_between(start_date="-1y", end_date="today"),
            )
        self.stdout.write(self.style.SUCCESS("Transactions created successfully."))
