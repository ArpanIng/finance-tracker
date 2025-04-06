from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .choices import TransactionTextChoices
from .models import Category


@receiver(post_save, sender=get_user_model())
def create_default_categories_for_user(sender, instance, created, **kwargs):
    """
    Create default categories for new registered user
    """
    if created:
        # income categories
        Category.objects.create(
            name="Salary", user=instance, type=TransactionTextChoices.INCOME
        )
        Category.objects.create(
            name="Parents", user=instance, type=TransactionTextChoices.INCOME
        )
        Category.objects.create(
            name="Investment", user=instance, type=TransactionTextChoices.INCOME
        )
        # expense categories
        Category.objects.create(
            name="Foods", user=instance, type=TransactionTextChoices.EXPENSE
        )
        Category.objects.create(
            name="Rent", user=instance, type=TransactionTextChoices.EXPENSE
        )
        Category.objects.create(
            name="Groceries", user=instance, type=TransactionTextChoices.EXPENSE
        )
