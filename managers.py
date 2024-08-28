from django.db.models import Manager, QuerySet, Q
from django.utils import timezone


class SoftDeletableQuerySet(QuerySet):
    def active(self):
        return self.filter(Q(_deletion_date=None) | Q(_deletion_date__gt=timezone.now()))

    def deleted(self):
        return self.filter(_deletion_date__lte=timezone.now())


class SoftDeletableManager(Manager):
    def get_queryset(self):
        return SoftDeletableQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def deleted(self):
        return self.get_queryset().deleted()
