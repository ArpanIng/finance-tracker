from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def activate_account(self):
        """Reactivates the account."""
        self.is_active = True
        # specifying fields to update
        self.save(update_fields=["is_active"])

    def deactivate_account(self):
        """Temporarily deactivates the account."""
        self.is_active = False
        # specifying fields to update
        self.save(update_fields=["is_active"])
