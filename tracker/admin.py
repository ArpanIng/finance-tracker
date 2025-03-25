from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "type", "created_at", "updated_at"]
    list_filter = ["type"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "note",
        "category",
        "amount",
        "type",
        "date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["type"]
