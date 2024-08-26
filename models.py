from django.db import models


class SoftDeletableModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    _is_deleted = models.BooleanField(_("Is "), default=False, db_index=True, editable=False)
    _deactivation_date = models.DateTimeField(blank=True, null=True, db_index=True, editable=False)
    related_deactivables = []

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
            if self.related_deactivables:
                for related_deactivable_field in self.related_deactivables:
                    try:
                        related_deactivable_set = getattr(self, related_deactivable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_deactivable in related_deactivable_set.all():
                            related_deactivable.deactivate(save)

    def activate(self, save: bool = True):
        """
        :param save:If True, the object will be saved after activation
        :return:None if save is False, otherwise the save method result (boolean)
        """
        self._deactivation_date = None
        if save:
            self.save()
            if self.related_deactivables:
                for related_deactivable_field in self.related_deactivables:
                    try:
                        related_deactivable_set = getattr(self, related_deactivable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_deactivable in related_deactivable_set.all():
                            related_deactivable.activate(save)

    @property
    def is_active(self):
        return self._deactivation_date is None or self._deactivation_date > timezone.now()

    @property
    def deactivation_date(self):
        return self._deactivation_date
