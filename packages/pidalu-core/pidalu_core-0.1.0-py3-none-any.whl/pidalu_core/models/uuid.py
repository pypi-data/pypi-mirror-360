import uuid
from django.db import models


class UUIDPrimaryKeyModel(models.Model):
    """
    Abstract base class that uses a UUID as the primary key.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
