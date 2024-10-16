from django import forms

from .models import Category, Transaction


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "type"]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["note", "description", "type", "category", "amount", "date"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.none()

        if "type" in self.data:
            # retrieve the type from the submitted data
            transaction_type = self.data.get("type")
            self.fields["category"].queryset = Category.objects.filter(
                user=user, type=transaction_type
            )
        # editing an existing instance
        elif self.instance.pk:
            self.fields["category"].queryset = Category.objects.filter(
                user=user, type=self.instance.type
            )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount
