from django.db.models import Sum

from .models import Category, Transaction

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


def get_transaction_chart_data(qs):
    count_per_category = (
        qs.order_by("category").values("category").annotate(total=Sum("amount"))
    )
    category_pks = count_per_category.values_list("category", flat=True)
    total_amounts = count_per_category.values_list("total", flat=True)
    categories = (
        Category.objects.filter(pk__in=category_pks)
        .values_list("name", flat=True)
        .order_by("pk")
    )
    return list(categories), list(total_amounts)
