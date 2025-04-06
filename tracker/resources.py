from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Category, Transaction


class TransactionResource(resources.ModelResource):
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="name"),
    )
    type = fields.Field()

    class Meta:
        model = Transaction
        fields = [
            "note",
            "description",
            "category",
            "type",
            "amount",
            "date",
            "created_at",
            "updated_at",
        ]

    def dehydrate_type(self, obj):
        if obj:
            return obj.get_type_display()
