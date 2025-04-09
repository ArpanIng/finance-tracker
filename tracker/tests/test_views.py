from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse

from tracker.choices import TransactionTextChoices
from tracker.models import Category, Transaction
from tracker.tests.factories import CategoryFactory, TransactionFactory
from tracker.views import (
    CategoryDeleteView,
    CategoryUpdateView,
    TransactionDeleteView,
    TransactionTotalStatisticsView,
    TransactionUpdateView,
)
from users.factories import UserFactory

User = get_user_model()

INCOME = TransactionTextChoices.INCOME
EXPENSE = TransactionTextChoices.EXPENSE
PASSWORD = "testpassword"


class IndexViewTest(SimpleTestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("tracker:index"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("tracker:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracker/index.html")


class TransactionListViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.name_url = reverse("tracker:transaction_list")
        self.client.login(email=self.user.email, password=PASSWORD)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.name_url)
        self.assertRedirects(
            response, "/accounts/login/?next=/transactions/", status_code=302
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/transactions/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.name_url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.name_url)
        self.assertTemplateUsed(response, "tracker/transaction_list.html")


class TransactionCreateViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.category = CategoryFactory(user=self.user)
        self.name_url = reverse("tracker:transaction_create")
        self.success_url = reverse("tracker:transaction_list")
        self.client.login(email=self.user.email, password=PASSWORD)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.name_url)
        self.assertRedirects(
            response, "/accounts/login/?next=/transactions/new/", status_code=302
        )

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.name_url)
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        form_data = {
            "note": "new transaction",
            "category": self.category.id,
            "type": INCOME,
            "amount": Decimal("100"),
            "date": date.today(),
        }
        response = self.client.post(self.name_url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.success_url, 302)
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.get(note="new transaction")
        self.assertEqual(transaction.user, self.user)


class TransactionUpdateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner_user = UserFactory()
        self.non_owner_user = UserFactory()
        self.transaction = TransactionFactory(user=self.owner_user)

        self.name_url = "tracker:transaction_update"
        self.url = reverse(self.name_url, kwargs={"pk": self.transaction.pk})

    def test_get_context_data(self):
        request = self.factory.get(self.url)
        request.user = self.owner_user

        view = TransactionUpdateView()
        view.request = request
        view.kwargs = {"pk": self.transaction.pk}
        view.object = self.transaction

        context = view.get_context_data()
        self.assertEqual(context["form_action_url"], self.url)

    def test_test_func_owner(self):
        request = self.factory.get(self.url)
        request.user = self.owner_user

        view = TransactionUpdateView()
        view.request = request
        view.kwargs = {"pk": self.transaction.pk}
        view.object = self.transaction

        self.assertTrue(view.test_func())

    def test_test_func_non_owner(self):
        request = self.factory.get(self.url)
        request.user = self.non_owner_user

        view = TransactionUpdateView()
        view.request = request
        view.kwargs = {"pk": self.transaction.pk}
        view.object = self.transaction

        self.assertFalse(view.test_func())


class TransactionDeleteViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner = UserFactory()
        self.non_owner = UserFactory()
        self.transaction = TransactionFactory(user=self.owner)

        self.name_url = "tracker:transaction_delete"
        self.url = reverse(self.name_url, kwargs={"pk": self.transaction.pk})

    def test_test_func_owner(self):
        request = self.factory.get(self.url)
        request.user = self.owner

        view = TransactionDeleteView()
        view.request = request
        view.kwargs = {"pk": self.transaction.pk}
        view.object = self.transaction

        self.assertTrue(view.test_func())

    def test_test_func_non_owner(self):
        request = self.factory.get(self.url)
        request.user = self.non_owner

        view = TransactionDeleteView()
        view.request = request
        view.kwargs = {"pk": self.transaction.pk}
        view.object = self.transaction

        self.assertFalse(view.test_func())

class TransactionStatisticsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.name_url = reverse('tracker:transaction_statistics')

        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.transactions = TransactionFactory(user=self.user).create_batch(5)
    
    def test_get_queryset(self):
        for t in self.transactions:
            print(f"{t}: {t.date}")



class TransactionTotalStatisticsViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.name_url = reverse("tracker:transaction_total_statistics")

        self.current_year = datetime.now().year
        self.transaction_this_year = TransactionFactory(
            user=self.user, date=date(self.current_year, 1, 1)
        )
        self.transaction_year_2024 = TransactionFactory(
            user=self.user, date=date(2024, 1, 1)
        )
        self.transaction_other_user = TransactionFactory(
            date=date(self.current_year, 5, 10)
        )

    def test_get_queryset_current_year(self):
        request = self.factory.get(self.name_url)
        request.user = self.user

        view = TransactionTotalStatisticsView()
        view.request = request

        queryset = view.get_queryset()
        self.assertIn(self.transaction_this_year, queryset)
        self.assertNotIn(self.transaction_year_2024, queryset)
        self.assertNotIn(self.transaction_other_user, queryset)

    def test_get_queryset_with_year_param(self):
        request = self.factory.get(f"{self.name_url}?year=2024")
        request.user = self.user

        view = TransactionTotalStatisticsView()
        view.request = request

        queryset = view.get_queryset()
        self.assertIn(self.transaction_year_2024, queryset)
        self.assertNotIn(self.transaction_this_year, queryset)
        self.assertNotIn(self.transaction_other_user, queryset)

    def test_get_context_data(self):
        pass


class CategoryCreateViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.name_url = reverse("tracker:category_create")
        self.success_url = reverse("tracker:manage")
        self.client.login(email=self.user.email, password=PASSWORD)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.name_url)
        self.assertRedirects(
            response, "/accounts/login/?next=/categories/new/", status_code=302
        )

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.name_url)
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        # Clean existing category to ensure unique name
        Category.objects.filter(name="Salary", user=self.user, type=INCOME).delete()
        form_data = {
            "name": "Salary",
            "type": INCOME,
        }
        response = self.client.post(self.name_url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.success_url, 302)
        category = Category.objects.get(name="Salary")
        self.assertEqual(category.user, self.user)


class CategoryUpdateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner_user = UserFactory()
        self.non_owner_user = UserFactory()
        self.category = CategoryFactory(user=self.owner_user)
        self.name_url = "tracker:category_update"
        self.url = reverse(self.name_url, kwargs={"pk": self.category.pk})

    def test_get_context_data(self):
        request = self.factory.get(self.url)
        request.user = self.owner_user

        view = CategoryUpdateView()
        view.request = request
        view.object = self.category
        context = view.get_context_data()
        self.assertEqual(context["form_action_url"], self.url)

    def test_test_func_for_owner(self):
        request = self.factory.get(self.url)
        request.user = self.owner_user

        view = CategoryUpdateView()
        view.request = request
        view.kwargs = {"pk": self.category.pk}
        view.object = self.category
        self.assertTrue(view.test_func())

    def test_test_func_for_non_owner(self):
        request = self.factory.get(self.url)
        request.user = self.non_owner_user

        view = CategoryUpdateView()
        view.request = request
        view.kwargs = {"pk": self.category.pk}
        view.object = self.category
        self.assertFalse(view.test_func())


class CategoryDeleteViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner_user = UserFactory()
        self.non_owner_user = UserFactory()
        self.category = CategoryFactory(user=self.owner_user)
        self.name_url = "tracker:category_delete"
        self.url = reverse(self.name_url, kwargs={"pk": self.category.pk})

    def test_test_func_for_owner(self):
        request = self.factory.get(self.url)
        request.user = self.owner_user

        view = CategoryDeleteView()
        view.request = request
        view.kwargs = {"pk": self.category.pk}
        view.object = self.category
        self.assertTrue(view.test_func())

    def test_test_func_for_non_owner(self):
        request = self.factory.get(self.url)
        request.user = self.non_owner_user

        view = CategoryDeleteView()
        view.request = request
        view.kwargs = {"pk": self.category.pk}
        view.object = self.category
        self.assertFalse(view.test_func())
