from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import FloatField, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView

from .filters import (
    TransactionChartFilter,
    TransactionFilter,
    TransactionStasticsFilter,
)
from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction, TransactionTextChoices
from .utils import get_transaction_chart_data


class IndexView(TemplateView):
    template_name = "tracker/index.html"


class TransactionListView(LoginRequiredMixin, FilterView):
    model = Transaction
    context_object_name = "transactions"
    filterset_class = TransactionFilter
    template_name = "tracker/transaction_list.html"

    def get_queryset(self):
        user = self.request.user
        # Retrieve query parameters
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


class TransactionChartsView(LoginRequiredMixin, FilterView):
    """Display chart based on the year and month."""

    model = Transaction
    filterset_class = TransactionChartFilter
    template_name = "tracker/transaction_chart.html"

    def get_queryset(self):
        user = self.request.user
        # Retrieve query parameters
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


class TransactionStatsTotalView(LoginRequiredMixin, View):
    template_name = "tracker/transaction_statistics.html"

    def get(self, request, *args, **kwargs):
        user = self.request.user
        total_balance = Transaction.objects.total_balance(user)
        year = self.request.GET.get("year", datetime.now().year)
        transaction_filter = TransactionStasticsFilter()
        monthly_totals = (
            Transaction.objects.filter(date__year=year)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(
                total_income=Sum(
                    "amount",
                    filter=Q(type=TransactionTextChoices.INCOME),
                    output_field=FloatField(),
                    default=0,
                ),
                total_expense=Sum(
                    "amount",
                    filter=Q(type=TransactionTextChoices.EXPENSE),
                    output_field=FloatField(),
                    default=0,
                ),
            )
        )
        incomes = monthly_totals.values_list("total_income", flat=True)
        expenses = monthly_totals.values_list("total_expense", flat=True)

        context = {
            "total_balance": total_balance,
            "monthly_totals": monthly_totals,
            "incomes": incomes,
            "expenses": expenses,
            "filter": transaction_filter,
        }
        return render(request, self.template_name, context)


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


def check_category_name(request):
    if request.method == "GET":
        user = request.user
        name = request.GET.get("name", None)
        exists = Category.objects.filter(user=user, name=name).exists()
        return JsonResponse({"exists": exists})
    return JsonResponse({"error": "Invalid request"}, status=400)


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
    user = request.user
    transaction_type = request.GET.get("type")
    categories = Category.objects.filter(user=user, type=transaction_type).values(
        "id", "name"
    )
    return JsonResponse(list(categories), safe=False)
