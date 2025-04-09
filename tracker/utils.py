from datetime import datetime

from django.db.models import QuerySet, Sum

from .models import Category

MONTH_CHOICES = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
]
current_year = datetime.now().year
YEAR_CHOICES = [(year, year) for year in range(2020, current_year + 6)]


def get_transaction_chart_data(qs: QuerySet):
    sum_per_category = (
        qs.values("category").annotate(total=Sum("amount")).order_by("-total")
    )
    category_pks = sum_per_category.values_list("category", flat=True)
    category_totals = sum_per_category.values_list("total", flat=True)
    categories = Category.objects.filter(pk__in=category_pks).values_list(
        "name", flat=True
    )
    return list(categories), list(category_totals)
