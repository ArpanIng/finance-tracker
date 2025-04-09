import factory

from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda obj: "{}.example.com".format(obj.username))
    password = factory.django.Password("testpassword")
