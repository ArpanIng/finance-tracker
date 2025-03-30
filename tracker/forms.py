from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Transaction


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type"]

    def __init__(self, *args, **kwargs):
        # access user from kwargs
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name:
            name = name.capitalize()
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        type = cleaned_data.get("type")

        if self.user and name and type:
            if Category.objects.filter(name=name, user=self.user, type=type).exists():
                raise ValidationError(
                    "Category with this Name and Type already exists."
                )

        return cleaned_data


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["note", "description", "type", "category", "amount", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.none()

        if "type" in self.data:
            # retrieve the type from the submitted data
            transaction_type = self.data.get("type")
            self.fields["category"].queryset = Category.objects.filter(
                user=self.user, type=transaction_type
            )
        # editing an existing instance
        elif self.instance.pk:
            self.fields["category"].queryset = Category.objects.filter(
                user=self.user, type=self.instance.type
            )

    def clean_amount(self):
        """Check the amount field is non-negative."""
        amount = self.cleaned_data["amount"]
        if amount < 0:
            raise ValidationError("Amount must be a positive number.")
        return amount
