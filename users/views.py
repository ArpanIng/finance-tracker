import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import View, TemplateView
from django.views.generic import FormView


from .forms import EmailConfirmationForm, AccountActivationForm

User = get_user_model()

logger = logging.getLogger(__name__)


class SettingView(LoginRequiredMixin, TemplateView):
    template_name = "users/accounts/settings.html"


class AccountDeactivateView(LoginRequiredMixin, FormView):
    """View to deactivate request user account."""

    form_class = EmailConfirmationForm
    template_name = "users/accounts/account_deactivate.html"
    success_url = reverse_lazy("users:account_deactivate_done")

    def form_valid(self, form):
        user = self.request.user
        submitted_email = form.cleaned_data["email"]

        # Check if the submitted email matches the user's email
        if submitted_email == user.email:
            user.deactivate_account()
            logout(self.request)
            messages.success(self.request, "Your account has been deactivated.")
            logger.info(f"Account deactivated for user: {user}")
            self.send_deactivation_email(user=user)
            return super().form_valid(form)
        else:
            form.add_error("email", "The submitted email does not match your email.")
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # pass extra user kwargs
        kwargs["user"] = self.request.user
        return kwargs

    def send_deactivation_email(self, user):
        subject = "Account Deactivated"
        body = render_to_string(
            "users/accounts/account_deactivate_done.txt",
            {
                "username": user.username,
                "support_team_name": settings.SUPPORT_TEAM_NAME,
            },
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.SUPPORT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class AccountDeactivateDoneView(TemplateView):
    """View to display success account deactivation."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    template_name = "users/accounts/account_deactivate_done.html"


class AccountActivateRequestView(FormView):
    """
    Allows a user to activate their account by generating a one-time use link that can be used to activate the account,
    and sending that link to the user’s registered email address.
    This view will send an email if:
    - The email address provided exists in the system.
    - The `is_active` field is false.
    """

    template_name = "users/accounts/account_activate_form.html"
    form_class = AccountActivationForm
    success_url = reverse_lazy("users:account_activate_done")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            form.add_error("email", "Invalid email")
            return self.form_invalid(form)
        self.send_activation_mail(user=user)
        return super().form_valid(form)

    def send_activation_mail(self, user):
        current_site = get_current_site(self.request)
        domain = current_site.domain
        protocol = "https" if self.request.is_secure() else "http"

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        subject = "Activate Your Account"
        body = render_to_string(
            "users/accounts/account_activate_email.html",
            {
                "protocol": protocol,
                "domain": domain,
                "uid": uid,
                "token": token,
                "app_name": settings.APP_NAME,
                "support_team_name": settings.SUPPORT_TEAM_NAME,
            },
        )
        send_mail(
            subject,
            body,
            settings.SUPPORT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class AccountActivateRequestDoneView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    template_name = "users/accounts/account_activate_done.html"


class AccountActivateConfirmView(View):
    """View to confirm user account activation."""

    template_name = "users/accounts/account_activate_confirm.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uidb64, token, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.activate_account()
            messages.success(request, "Your account has been activated successfully.")
            return redirect("account_login")
        else:
            messages.error(request, "The activation link is invalid or has expired.")
            return render(request, self.template_name)


class AccountDeleteView(LoginRequiredMixin, FormView):
    """View to delete request user account."""

    form_class = EmailConfirmationForm
    template_name = "users/accounts/account_delete.html"
    success_url = settings.LOGOUT_REDIRECT_URL

    def form_valid(self, form):
        user = self.request.user
        submitted_email = form.cleaned_data["email"]

        # Check if the submitted email matches the user's email
        if submitted_email == user.email:
            user.delete()
            logout(self.request)
            messages.success(self.request, "Your account is deleted.")
            self.send_delete_confirmation_mail(user=user)
            return super().form_valid(form)
        else:
            form.add_error("email", "The submitted email does not match your email.")
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # pass extra user kwargs
        kwargs["user"] = self.request.user
        return kwargs

    def send_delete_confirmation_mail(self, user):
        subject = f"{settings.APP_NAME} Account Deletion Confirmation"
        body = render_to_string(
            "users/accounts/account_delete_confirmation.txt",
            {
                "support_team_name": settings.SUPPORT_TEAM_NAME,
            },
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.SUPPORT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
