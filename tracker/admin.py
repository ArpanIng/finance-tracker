from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "type", "created_at", "updated_at"]
    list_filter = ["type"]


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = [
        "note",
        "category",
        "user",
        "amount",
        "type",
        "date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["type"]
