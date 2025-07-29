from django.db import models
from django.forms.models import model_to_dict


class AuditModel(models.Model):
    """
    Mixin to track field changes on save. Override `log_changes()` to persist them.
    """

    _original_state = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_state = self._current_state()

    def _current_state(self):
        """
        Returns a dict of the current model field values.
        """
        return model_to_dict(self, fields=[f.name for f in self._meta.fields])

    def get_field_changes(self) -> dict:
        """
        Returns a dict of changed fields: {field: (old_value, new_value)}
        """
        changes = {}
        current = self._current_state()

        for field, old_value in self._original_state.items():
            new_value = current.get(field)
            if old_value != new_value:
                changes[field] = (old_value, new_value)

        return changes

    def save(self, *args, **kwargs):
        changes = self.get_field_changes()

        if changes:
            self.log_changes(changes)

        super().save(*args, **kwargs)
        self._original_state = self._current_state()

    def log_changes(self, changes: dict):
        """
        Override this method to persist or log changes.
        """
        print(f"[AuditModel] {self.__class__.__name__} changes: {changes}")
