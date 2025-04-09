from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("accounts/settings/", views.SettingView.as_view(), name="settings"),
    path(
        "accounts/deactivate/",
        views.AccountDeactivateView.as_view(),
        name="account_deactivate",
    ),
    path(
        "accounts/deactivate/done/",
        views.AccountDeactivateDoneView.as_view(),
        name="account_deactivate_done",
    ),
    path(
        "accounts/activate/",
        views.AccountActivateRequestView.as_view(),
        name="account_activate",
    ),
    path(
        "accounts/activate/done/",
        views.AccountActivateRequestDoneView.as_view(),
        name="account_activate_done",
    ),
    path(
        "accounts/activate/<uidb64>/<token>/",
        views.AccountActivateConfirmView.as_view(),
        name="account_activate_confirm",
    ),
    path(
        "accounts/delete/",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
]
