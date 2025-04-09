import factory

from users.factories import UserFactory

from ..choices import TransactionTextChoices
from ..models import Category, Transaction

DEFAULT_CATEGORIES = ["Salary", "Parents", "Investment", "Foods", "Rent", "Groceries"]


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name", "user", "type")

    name = factory.Iterator(DEFAULT_CATEGORIES)
    user = factory.SubFactory(UserFactory)
    type = factory.Iterator(TransactionTextChoices.values)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    note = factory.Faker("sentence")
    category = factory.SubFactory(CategoryFactory)
    user = factory.SubFactory(UserFactory)
    type = factory.Iterator(TransactionTextChoices.values)
    amount = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    date = factory.Faker("date_this_decade")
