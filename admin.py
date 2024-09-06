import reversion
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BaseSoftdeletableAdmin(admin.ModelAdmin):
    _model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = self.get_model()

    @staticmethod
    def get_model():
        pass


class AvailableAdmin(BaseSoftdeletableAdmin):
    actions = ["softdelete"]

    def get_queryset(self, request):
        return self._model.objects.available()

    @staticmethod
    def get_model():
        raise NotImplementedError("You must implement get_model method")

    @admin.action(description=_("Softdelete selected objects"))
    def softdelete(self, request, queryset):
        for obj in queryset:
            try:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(_("Object softdeleted"))
                    obj.softdelete()
            except NameError as e:
                obj.softdelete()


class SoftdeletedAdmin(BaseSoftdeletableAdmin):
    actions = ["restore"]

    def get_queryset(self, request):
        return self._model.objects.softdeleted()

    @staticmethod
    def get_model():
        raise NotImplementedError("You must implement get_model method")

    @admin.action(description=_("Restore selected objects"))
    def restore(self, request, queryset):
        for obj in queryset:
            try:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(_("Object restored"))
                    obj.restore()
            except NameError:
                obj.restore()
