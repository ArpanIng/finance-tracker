from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import FloatField, Q
from django.db.models.functions import TruncYear, TruncMonth
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django_filters.views import FilterView

from .utils import get_transaction_chart_data
from .forms import TransactionForm
from .filters import (
    TransactionFilter,
    TransactionChartFilter,
    TransactionStasticsFilter,
)
from .models import Transaction


class IndexView(TemplateView):
    template_name = "tracker/index.html"


from django.db.models import Sum
from datetime import datetime


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
        print("-----------")
        print(totals)
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
        context["test"] = "working"
        context["form_action_url"] = form_action_url
        return context


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
                    filter=Q(type=Transaction.TransactionTextChoices.INCOME),
                    output_field=FloatField(),
                    default=0,
                ),
                total_expense=Sum(
                    "amount",
                    filter=Q(type=Transaction.TransactionTextChoices.EXPENSE),
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
