from django.conf import settings


class ReadOnlyAdminFieldsMixin:
    """
    Mixin to make specified fields read-only in Django Admin.
    Override `readonly_admin_fields` in your model admin.
    """

    readonly_admin_fields = ()

    def get_readonly_fields(self, request, obj=None):
        default = super().get_readonly_fields(request, obj)
        return default + tuple(self.readonly_admin_fields or [])


class AutoSlugAdminMixin:
    """
    Mixin to auto-fill the slug field based on model's slug_source_field
    or global default PIDALU_CORE_AUTO_SLUG_FIELD.
    """

    def get_prepopulated_fields(self, request, obj=None):
        default = super().get_prepopulated_fields(request, obj)
        source = getattr(
            obj,
            "slug_source_field",
            getattr(settings, "PIDALU_CORE_AUTO_SLUG_FIELD", "name"),
        )
        return {**default, "slug": (source,)} if hasattr(obj, source) else default
