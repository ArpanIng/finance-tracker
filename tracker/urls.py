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
        "transactions/statistics/",
        views.TransactionStatisticsView.as_view(),
        name="transaction_statistics",
    ),
    path(
        "transactions/total-statistics/",
        views.TransactionTotalStatisticsView.as_view(),
        name="transaction_total_statistics",
    ),
    path(
        "transactions/export/",
        views.TransactionExportView.as_view(),
        name="transaction_export",
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
    path("load-categories/", views.load_categories, name="load_categories"),
]
