from django import forms

from .models import Category, Transaction


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type"]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["note", "category", "type", "amount", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount
