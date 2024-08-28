from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from softdeletable.managers import SoftDeletableManager


class SoftDeletableModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    _is_deleted = models.BooleanField(_("Is "), default=False, db_index=True, editable=False)
    _deletion_date = models.DateTimeField(blank=True, null=True, db_index=True, editable=False)
    related_softdeletables = []

    class Meta:
        abstract = True

    objects = SoftDeletableManager()

    def deactivate(self, save: bool = True, deactivation_date: timezone.datetime = None):
        """
        :param deactivation_date:If not provided, ''deactivation_date'' = datetime.now(timezone.utc)
        :param save:If True, the object will be saved after deactivation
        :return:None
        """
        self._deactivation_date = timezone.now() if deactivation_date is None else deactivation_date
        if save:
            self.save()
            if self.related_softdeletables:
                for related_softdeletable_field in self.related_softdeletables:
                    try:
                        related_softdeletable_set = getattr(self, related_softdeletable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_deactivable in related_softdeletable_set.all():
                            related_deactivable.deactivate(save)

    def activate(self, save: bool = True):
        """
        :param save:If True, the object will be saved after activation
        :return:None if save is False, otherwise the save method result (boolean)
        """
        self._deactivation_date = None
        if save:
            self.save()
            if self.related_softdeletables:
                for related_softdeletable_field in self.related_softdeletables:
                    try:
                        related_softdeletable_set = getattr(self, related_softdeletable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_softdeletable in related_softdeletable_set.all():
                            related_softdeletable.activate(save)

    @property
    def is_active(self):
        return self._deletion_date is None or self._deletion_date > timezone.now()

    @property
    def deletion_date(self):
        return self._deletion_date
