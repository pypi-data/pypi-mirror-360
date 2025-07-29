from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True)

    def hard_delete(self):
        return super().delete()

    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def all_with_deleted(self):
        return self.all()


class SoftDeleteManager(models.Manager):
    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db)

    def active(self) -> SoftDeleteQuerySet:
        return self.get_queryset().active()

    def only_deleted(self) -> SoftDeleteQuerySet:
        return self.get_queryset().deleted()

    def with_deleted(self) -> SoftDeleteQuerySet:
        return self.get_queryset().all_with_deleted()


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    # Default manager only shows active
    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        super().delete()
