import reversion
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


from softdeletable.managers import SoftdeletableManager


class SoftDeletableModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    _softdeletion_date = models.DateTimeField(blank=True, null=True, db_index=True, editable=False)
    _is_softdeleted = models.BooleanField(default=False, db_index=True, editable=False)
    _is_restored = models.BooleanField(default=False, editable=False)
    related_softdeletables = []

    class Meta:
        abstract = True

    objects = SoftdeletableManager()

    def get_related_softdeletables(self):
        return self.related_softdeletables

    def softdelete(self, save: bool = True, deletion_date: timezone.datetime = None, user=None):
        """
        :param deletion_date:If not provided, ''deletion_date'' = datetime.now(timezone.utc)
        :param save:If True, the object will be saved after deactivation
        :param user:User that softdeletes the object
        :return:None
        """
        if self.is_softdeleted:
            return False

        self._softdeletion_date = timezone.now() if deletion_date is None else deletion_date
        self._is_softdeleted = True
        self._is_restored = False
        if save:
            print("Saving")
            with reversion.create_revision():
                if user:
                    reversion.set_user(user)
                reversion.set_comment(_("Object softdeleted"))
                self.save()
            if self.get_related_softdeletables():
                for related_softdeletable_field in self.get_related_softdeletables():
                    try:
                        related_softdeletable_set = getattr(self, related_softdeletable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_softdeletable in related_softdeletable_set.all():
                            related_softdeletable.softdelete(True)
        return True

    def restore(self, save: bool = True, user=None):
        """
        :param save:If True, the object will be saved after
        :param user:User that restores the object
        :return:None if save is False, otherwise the save method result (boolean)
        """
        if self.is_softdeleted:
            self._is_restored = True if self.is_softdeleted else self.is_restored
            self._softdeletion_date = None
            self._is_softdeleted = False
            if save:
                if user:
                    with reversion.create_revision():
                        reversion.set_user(user)
                        reversion.set_comment(_("Object restored"))
                        self.save()
                if self.get_related_softdeletables():
                    for related_softdeletable_field in self.get_related_softdeletables():
                        try:
                            related_softdeletable_set = getattr(self, related_softdeletable_field)
                        except AttributeError:
                            continue
                        else:
                            for related_softdeletable in related_softdeletable_set.all():
                                related_softdeletable.activate(save)
            return True
        else:
            return False

    @property
    def is_softdeleted(self) -> bool:
        return self._is_softdeleted

    @property
    def is_available(self) -> bool:
        return self._softdeletion_date is None or self._softdeletion_date > timezone.now()

    @property
    def is_restored(self):
        return self._is_restored

    @property
    def softdeletion_date(self) -> timezone.datetime:
        return self._softdeletion_date
