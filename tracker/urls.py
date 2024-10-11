from django.urls import path

from . import views

app_name = "tracker"


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("manage/", views.ManageView.as_view(), name="manage"),
    path("transactions/", views.TransactionListView.as_view(), name="transaction_list"),
    path(
        "transactions/new/",
        views.TransactionCreateView.as_view(),
        name="transaction_create",
    ),
    path(
        "transactions/<int:pk>/edit/",
        views.TransactionUpdateView.as_view(),
        name="transaction_update",
    ),
    path(
        "transactions/<int:pk>/delete/",
        views.TransactionDeleteView.as_view(),
        name="transaction_delete",
    ),
    path(
        "transactions/charts/",
        views.TransactionChartsView.as_view(),
        name="transaction_charts",
    ),
    path(
        "transactions/stats/",
        views.TransactionStatsTotalView.as_view(),
        name="transaction_statistics",
    ),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    # validation urls
    path(
        "validate-category-name/",
        views.CategoryNameValidationView.as_view(),
        name="validate-category-name",
    ),
]
