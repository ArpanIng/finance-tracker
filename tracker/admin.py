from django.contrib import admin

from .models import User, Category, Transaction

admin.site.register(User)
admin.site.register(Category)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["note", "category", "amount", "type", "date"]
