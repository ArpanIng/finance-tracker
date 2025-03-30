import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView

from .filters import (
    TransactionFilter,
    TransactionStasticsFilter,
    TransactionTotalStasticsFilter,
)
from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction, TransactionTextChoices
from .utils import get_transaction_chart_data


logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = "tracker/index.html"


class TransactionListView(LoginRequiredMixin, FilterView):
    """List all transaction of the request user."""

    model = Transaction
    context_object_name = "transactions"
    filterset_class = TransactionFilter
    template_name = "tracker/transaction_list.html"

    def get_queryset(self):
        user = self.request.user
        # get query parameters, default to current year and month
        selected_year = self.request.GET.get("year", datetime.now().year)
        selected_month = self.request.GET.get("month", datetime.now().month)

        return (
            super()
            .get_queryset()
            .filter(user=user, date__year=selected_year, date__month=selected_month)
            .select_related("category")
        )

    def get_template_names(self):
        if self.request.htmx:
            return ["tracker/partials/transaction_container.html"]
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        totals = self.get_queryset().get_total_income_and_expense()
        total_incomes = totals["total_income"]
        total_expenses = totals["total_expense"]
        net_income = total_incomes - total_expenses
        context["total_incomes"] = total_incomes
        context["total_expenses"] = total_expenses
        context["net_income"] = net_income
        return context


class TransactionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Transaction
    context_object_name = "transaction"
    form_class = TransactionForm
    success_message = "Transaction created successfully."
    success_url = reverse_lazy("tracker:transaction_list")
    template_name = "tracker/transaction_form.html"

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.user = self.request.user
        transaction.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_action_url = reverse("tracker:transaction_create")
        context["form_action_url"] = form_action_url
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class TransactionUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Transaction
    context_object_name = "transaction"
    form_class = TransactionForm
    success_url = reverse_lazy("tracker:transaction_list")
    success_message = "Transaction updated successfully."
    template_name = "tracker/transaction_form.html"

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.object
        form_action_url = reverse(
            "tracker:transaction_update", kwargs={"pk": transaction.pk}
        )
        context["form_action_url"] = form_action_url
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class TransactionDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Transaction
    context_object_name = "transaction"
    success_url = reverse_lazy("tracker:transaction_list")
    success_message = "Transaction deleted successfully."
    template_name = "tracker/transaction_delete.html"

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class TransactionStatisticsView(LoginRequiredMixin, FilterView):
    """Display monthly transaction chart stats."""

    model = Transaction
    filterset_class = TransactionStasticsFilter
    template_name = "tracker/transaction_statistics.html"

    def get_queryset(self):
        user = self.request.user
        # Retrieve query parameters, default to current year and month
        selected_year = self.request.GET.get("year", datetime.now().year)
        selected_month = self.request.GET.get("month", datetime.now().month)

        return (
            super()
            .get_queryset()
            .filter(user=user, date__year=selected_year, date__month=selected_month)
            .select_related("category")
        )

    def get_template_names(self):
        if self.request.htmx:
            return ["tracker/partials/chart_container.html"]
        return self.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_queryset()
        income_categories, income_totals = get_transaction_chart_data(
            transactions.filter(type="INC"),
        )
        expense_categories, expense_totals = get_transaction_chart_data(
            transactions.filter(type="EXP"),
        )
        income_data = [
            {"category": cat, "amount": amt}
            for cat, amt in zip(income_categories, income_totals)
        ]
        expense_data = [
            {"category": cat, "amount": amt}
            for cat, amt in zip(expense_categories, expense_totals)
        ]

        context["income_categories"] = income_categories
        context["income_totals"] = income_totals
        context["expense_categories"] = expense_categories
        context["expense_totals"] = expense_totals
        context["income_data"] = income_data
        context["expense_data"] = expense_data
        return context


class TransactionTotalStatisticsView(LoginRequiredMixin, FilterView):
    """Display total yearly transaction chart stats."""

    filterset_class = TransactionTotalStasticsFilter
    template_name = "tracker/transaction_total_statistics.html"

    def get_queryset(self):
        user = self.request.user
        # get query parameters, default to current year
        year = self.request.GET.get("year", datetime.now().year)
        return Transaction.objects.filter(user=user, date__year=year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        total_yearly_balance = queryset.total_balance()
        yearly_totals = queryset.get_total_income_and_expense()
        total_yearly_incomes = yearly_totals["total_income"]
        total_yearly_expenses = yearly_totals["total_expense"]
        monthly_totals = queryset.get_monthly_totals()
        total_incomes_per_month = monthly_totals.values_list("total_income", flat=True)
        total_expenses_per_month = monthly_totals.values_list(
            "total_expense", flat=True
        )

        context["total_yearly_balance"] = total_yearly_balance
        context["total_yearly_incomes"] = total_yearly_incomes
        context["total_yearly_expenses"] = total_yearly_expenses
        context["total_incomes_per_month"] = total_incomes_per_month
        context["total_expenses_per_month"] = total_expenses_per_month
        return context


class ManageView(LoginRequiredMixin, View):
    template_name = "tracker/manage.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        categories = (
            Category.objects.filter(user=user).select_related("user").order_by("name")
        )
        income_categories = [
            category
            for category in categories
            if category.type == TransactionTextChoices.INCOME
        ]
        expense_categories = [
            category
            for category in categories
            if category.type == TransactionTextChoices.EXPENSE
        ]
        form = CategoryForm()

        context = {
            "income_categories": income_categories,
            "expense_categories": expense_categories,
            "income_categories_count": len(income_categories),
            "expense_categories_count": len(expense_categories),
            "form": form,
        }
        return render(request, self.template_name, context)


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    context_object_name = "category"
    form_class = CategoryForm
    success_url = reverse_lazy("tracker:manage")
    success_message = "Category created successfully."
    template_name = "tracker/category_form.html"

    def form_valid(self, form):
        category = form.save(commit=False)
        category.user = self.request.user
        category.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_action_url = reverse("tracker:category_create")
        context["form_action_url"] = form_action_url
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class CategoryUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Category
    context_object_name = "category"
    form_class = CategoryForm
    success_url = reverse_lazy("tracker:manage")
    success_message = "Category updated successfully."
    template_name = "tracker/category_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        form_action_url = reverse("tracker:category_update", kwargs={"pk": category.pk})
        context["form_action_url"] = form_action_url
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


class CategoryDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView
):
    model = Category
    context_object_name = "category"
    success_url = reverse_lazy("tracker:manage")
    success_message = "Category deleted successfully."
    template_name = "tracker/category_delete.html"

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user


def load_categories(request):
    """Return list of categories of the user based on the transaction type."""
    user = request.user
    transaction_type = request.GET.get("type")
    categories = Category.objects.filter(user=user, type=transaction_type).values(
        "id", "name"
    )
    return JsonResponse(list(categories), safe=False)
