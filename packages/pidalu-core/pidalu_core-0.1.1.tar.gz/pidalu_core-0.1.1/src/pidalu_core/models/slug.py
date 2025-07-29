from django.db import models
from django.utils.text import slugify
from django.conf import settings


class SlugFieldModel(models.Model):
    """
    Abstract model that auto-generates a slug field from a source field.
    You can override the source field by setting `slug_source_field` in the model.
    """

    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        abstract = True

    def get_slug_source_field(self):
        """
        Returns the name of the field to generate the slug from.
        Default: `settings.PIDALU_CORE_AUTO_SLUG_FIELD`, or 'name'.
        """
        return getattr(
            self,
            "slug_source_field",
            getattr(settings, "PIDALU_CORE_AUTO_SLUG_FIELD", "name"),
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            source_field = self.get_slug_source_field()
            source_value = getattr(self, source_field, None)

            if not source_value:
                model_name = self.__class__.__name__
                raise ValueError(
                    f"[pidalu_core] Could not generate slug for {model_name}: "
                    f"'{source_field}' field is missing or empty. "
                    f"Set `slug_source_field = '<your_field>'` in the model or configure PIDALU_CORE_AUTO_SLUG_FIELD."
                )

            self.slug = slugify(source_value)

        super().save(*args, **kwargs)
