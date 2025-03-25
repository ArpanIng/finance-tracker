import logging

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse


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
