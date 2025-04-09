import logging

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class AccountActivationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)


class EmailConfirmationForm(forms.Form):
    email = forms.EmailField(
        label="Please type in your email to confirm.", max_length=254
    )

    def __init__(self, *args, **kwargs):
        # access extra kwargs
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = f"{user.email}"
