import reversion
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class BaseSoftDeletableAdmin(admin.ModelAdmin):
    _model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._model = self.get_model()

    @staticmethod
    def get_model():
        pass


class ActiveAdmin(BaseSoftDeletableAdmin):
    actions = ["softdelete"]

    def get_queryset(self, request):
        return self._model.objects.active()

    @staticmethod
    def get_model():
        raise NotImplementedError("You must implement get_model method")

    @admin.action(description=_("Soft-delete selected objects"))
    def deactivate(self, request, queryset):
        for obj in queryset:
            try:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(_("Soft-deleted edition"))
                    obj.deactivate()
            except NameError as e:
                obj.deactivate()


class InactiveAdmin(BaseSoftDeletableAdmin):
    actions = ["reactivate"]

    def get_queryset(self, request):
        return self._model.objects.inactive()

    @staticmethod
    def get_model():
        raise NotImplementedError("You must implement get_model method")

    @admin.action(description=_("Reactivate selected objects"))
    def reactivate(self, request, queryset):
        for obj in queryset:
            try:
                with reversion.create_revision():
                    reversion.set_user(request.user)
                    reversion.set_comment(_("Reactivated edition"))
                    obj.activate()
            except NameError:
                obj.activate()
