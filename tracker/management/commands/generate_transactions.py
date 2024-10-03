import random
from faker import Faker
from django.core.management.base import BaseCommand

from tracker.models import User, Category, Transaction


class Command(BaseCommand):
    help = "Create dummy transactions"

    def handle(self, *args, **kwargs):
        fake = Faker()

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
        for category in category_list:
            Category.objects.get_or_create(name=category)
        self.stdout.write(
            self.style.SUCCESS(f"{len(category_list)} categories created.")
        )

        # get the user
        user = User.objects.filter(username="admin").first()
        if not user:
            user = User.objects.create_superuser(
                username="admin", password="superadmin"
            )

        categories = Category.objects.all()
        transaction_type_choices = [
            Transaction.TransactionTextChoices.INCOME,
            Transaction.TransactionTextChoices.EXPENSE,
        ]
        for i in range(20):
            transaction_type = random.choice(transaction_type_choices)
            Transaction.objects.create(
                note=fake.word(),
                category=random.choice(categories),
                user=user,
                type=transaction_type,
                amount=random.uniform(10, 2000),
                date=fake.date_between(start_date="-1y", end_date="today"),
            )
        self.stdout.write(self.style.SUCCESS("Transactions created successfully."))
