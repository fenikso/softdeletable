from django.db.models import Manager, QuerySet, Q
from django.utils import timezone


class SoftdeletableQuerySetMixin:
    def available(self):
        return self.filter(Q(_softdeletion_date=None) | Q(_softdeletion_date__gt=timezone.now()))

    def softdeleted(self):
        return self.filter(_softdeletion_date__lte=timezone.now())

    def softdelete(self):
        """
        Softdelete all the objects in the queryset
        """
        count = 0
        count_related = 0
        # TODO: return the number of objects softdeleted
        for obj in self:
            obj.softdelete()


class SoftdeletableQuerySet(SoftdeletableQuerySetMixin, QuerySet):
    pass


class SoftdeletableManagerMixin:
    def available(self):
        return self.get_queryset().available()

    def softdeleted(self):
        return self.get_queryset().softdeleted()


class SoftdeletableManager(SoftdeletableManagerMixin, Manager):
    def get_queryset(self):
        return SoftdeletableQuerySet(self.model, using=self._db)
