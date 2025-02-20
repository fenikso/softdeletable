from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

try:
    import reversion
    reversion_is_installed = True
except ModuleNotFoundError:
    reversion_is_installed = False


from softdeletable.managers import SoftDeletableManager

try:
    SOFTDELETE_RELATED = settings.SOFTDELETE_RELATED
except:
    SOFTDELETE_RELATED = False


class SoftDeletableModel(models.Model):
    """
    Abstract model that provides soft delete functionality.
    """
    _softdeletion_date = models.DateTimeField(blank=True, null=True, db_index=True, editable=False)
    _is_restored = models.BooleanField(default=False, editable=False)
    related_softdeletables = []

    class Meta:
        abstract = True
        permissions = [
            ("can_softdelete", _("Can softdelete object")),
            ("can_restore", _("Can restore object")),
        ]

    objects = SoftDeletableManager()

    def get_related_softdeletables(self):
        return self.related_softdeletables

    def softdelete(self, save: bool = False, deletion_date: timezone.datetime = None, also_related: bool = True, user: settings.AUTH_USER_MODEL = None) -> bool:
        """
        :param save:If True, the object will be saved after deactivation. If also_related = True, save turns to True. Defaults to False
        :param deletion_date:If not provided, ''deletion_date'' = datetime.now(timezone.utc)
        :param also_related:If True softdelete related softdeletables. Defaults to True
        :param user:User that softdeletes the object. Only when django-reversion is used
        :return:False if the object is already softdeleted or and error occurs, otherwise True
        """

        # TODO: related softdeletables? save them too? flag?

        if self._softdeletion_date is not None:
            return False

        save = save or also_related

        self._softdeletion_date = timezone.now() if deletion_date is None else deletion_date
        self._is_restored = False

        if save:
            if reversion_is_installed:
                with reversion.create_revision():
                    if user:
                        reversion.set_user(user)
                    reversion.set_comment(_("Object softdeleted"))
                    self.save()
            else:
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

    def restore(self, save: bool = True, also_related: bool = True, user: settings.AUTH_USER_MODEL = None) -> bool:
        """
        :param save:If True, the object will be saved after restoration. If also_related = True, save turns to True. Defaults to False
        :param also_related:If True restore related softdeletables. Defaults to True
        :param user:User that restores the object. Only when django-reversion is used
        :return:False if the object is already restored or and error occurs, otherwise True
        """
        if not self.is_softdeleted:
            return False

        self._is_restored = True
        self._softdeletion_date = None
        if save:
            if user:
                if reversion_is_installed:
                    with reversion.create_revision():
                        reversion.set_user(user)
                        reversion.set_comment(_("Object restored"))
                        self.save()
                else:
                    self.save()
            if self.get_related_softdeletables():
                for related_softdeletable_field in self.get_related_softdeletables():
                    try:
                        related_softdeletable_set = getattr(self, related_softdeletable_field)
                    except AttributeError:
                        continue
                    else:
                        for related_softdeletable in related_softdeletable_set.all():
                            related_softdeletable.restore(save)
        return True

    @property
    def is_softdeleted(self) -> bool:
        return self._softdeletion_date is not None and self._softdeletion_date <= timezone.now()

    @property
    def is_available(self) -> bool:
        return self._softdeletion_date is None or self._softdeletion_date > timezone.now()

    @property
    def is_restored(self) -> bool:
        return self._is_restored

    @property
    def softdeletion_date(self) -> timezone.datetime:
        return self._softdeletion_date
