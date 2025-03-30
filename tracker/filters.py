from datetime import datetime

import django_filters

from .models import Category, Transaction, TransactionTextChoices
from .utils import MONTH_CHOICES, YEAR_CHOICES


class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        choices=TransactionTextChoices.choices,
        field_name="type",
        label="Type:",
        empty_label="All",
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label="Category:",
        empty_label="All",
    )
    year = django_filters.ChoiceFilter(
        choices=YEAR_CHOICES,
        field_name="date",
        lookup_expr="year",
        label="Year:",
        empty_label=None,
    )
    month = django_filters.ChoiceFilter(
        choices=MONTH_CHOICES,
        field_name="date",
        lookup_expr="month",
        label="Month:",
        empty_label=None,
    )

    class Meta:
        model = Transaction
        fields = ["transaction_type", "category", "year", "month"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.initial["year"] = datetime.now().year
        self.form.initial["month"] = datetime.now().month


class TransactionStasticsFilter(django_filters.FilterSet):
    year = django_filters.ChoiceFilter(
        choices=YEAR_CHOICES,
        field_name="date",
        lookup_expr="year",
        label="Year:",
        empty_label=None,
    )
    month = django_filters.ChoiceFilter(
        choices=MONTH_CHOICES,
        field_name="date",
        lookup_expr="month",
        label="Month:",
        empty_label=None,
    )

    class Meta:
        model = Transaction
        fields = ["year", "month"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.initial["year"] = datetime.now().year
        self.form.initial["month"] = datetime.now().month


class TransactionTotalStasticsFilter(django_filters.FilterSet):
    year = django_filters.ChoiceFilter(
        choices=YEAR_CHOICES,
        field_name="date",
        lookup_expr="year",
        label="Year:",
        empty_label=None,
    )

    class Meta:
        model = Transaction
        fields = ["year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.initial["year"] = datetime.now().year
