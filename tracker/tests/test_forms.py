from django.contrib.auth import get_user_model
from django.test import TestCase

from tracker.choices import TransactionTextChoices
from tracker.forms import CategoryForm

INCOME = TransactionTextChoices.INCOME
EXPENSE = TransactionTextChoices.EXPENSE
User = get_user_model()


class CategoryFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john", email="john@example.com", password="lorempass"
        )

    # def test_form_kwargs(self):
    #     form = CategoryForm(user=self.user)
    #     print(form.__init__)
    #     self.assertEqual(form.user, self.user)

    def test_clean_name(self):
        form_data = {
            "name": "salary",
            "user": self.user,
            "type": "INC",
        }
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Salary")
