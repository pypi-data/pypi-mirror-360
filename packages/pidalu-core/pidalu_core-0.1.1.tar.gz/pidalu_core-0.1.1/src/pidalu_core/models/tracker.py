from django.db import models
from django.conf import settings
from django.utils import timezone

from pidalu_core.middleware.requests import get_current_user


class TimeStampedModel(models.Model):
    """
    Adds `created_at` and `updated_at` fields to a model.
    Automatically tracks creation and last modification times.
    """

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserTrackerModel(models.Model):
    """
    Adds `created_by` and `updated_by` fields to a model.
    These should be set automatically using middleware or overridden `save()`.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            if not self.pk and not self.created_by:
                self.created_by = user
            self.updated_by = user
        super().save(*args, **kwargs)


class TrackedModel(TimeStampedModel, UserTrackerModel):
    """
    Combines TimeStampedModel and UserTrackerModel for full tracking.
    """

    class Meta:
        abstract = True
