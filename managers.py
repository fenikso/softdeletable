from django.db.models import Manager, QuerySet, Q
from django.utils import timezone


class SoftDeletableQuerySetMixin:
    def available(self):
        return self.filter(Q(_softdeletion_date=None) | Q(_softdeletion_date__gt=timezone.now()))

    def softdeleted(self):
        return self.filter(_softdeletion_date__lte=timezone.now())

    def softdelete(self):
        """
        Softdelete all the objects in the queryset
        """
        count = 0
        for obj in self:
            if obj.softdelete():
                count += 1
        return count


class SoftDeletableQuerySet(SoftDeletableQuerySetMixin, QuerySet):
    pass


class SoftDeletableManagerMixin:
    def available(self):
        return self.get_queryset().available()

    def softdeleted(self):
        return self.get_queryset().softdeleted()


class SoftDeletableManager(SoftDeletableManagerMixin, Manager):
    def get_queryset(self):
        return SoftDeletableQuerySet(self.model, using=self._db)
