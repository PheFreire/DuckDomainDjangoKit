import copy

from django.db import (
    IntegrityError,
)
from django.db import models as django_models
from django.db import (
    transaction,
)
from django.contrib import (
    admin,
    messages,
)
from django.contrib.admin import (
    SimpleListFilter,
)


class DeletedAtFilter(SimpleListFilter):
    title = "Soft Delete"
    parameter_name = "deleted"

    def lookups(self, request, model_admin):
        return [
            ("no", "Not Deleted"),
            ("yes", "Deleted"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(deleted_at__isnull=True)
        elif self.value() == "yes":
            return queryset.filter(deleted_at__isnull=False)
        return queryset


class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = [DeletedAtFilter, "created_at", "updated_at"]
    readonly_fields = ["uuid", "deleted_at"]
    ordering = ["-created_at"]

    @admin.action()
    def soft_delete_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.deleted_at is None:
                obj.soft_delete()
                updated += 1
        self.message_user(
            request, f"{updated} item(ns) soft-deletado(s).", messages.SUCCESS
        )

    @admin.action()
    def restore_selected(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.deleted_at is not None:
                obj.restore()
                updated += 1
        self.message_user(
            request, f"{updated} item(ns) restaurado(s).", messages.SUCCESS
        )

    @admin.action()
    def duplicate_selected(self, request, queryset):
        unique_char_fields = self._get_unique_char_fields(queryset.model)
        created = 0
        failed = 0
        for obj in queryset:
            for attempt in range(1, 100):
                new_obj = copy.copy(obj)
                new_obj.pk = None
                new_obj.deleted_at = None
                suffix = " - Copy" if attempt == 1 else f" - Copy {attempt}"
                for field_name in unique_char_fields:
                    original_value = getattr(obj, field_name) or ""
                    setattr(new_obj, field_name, f"{original_value}{suffix}")
                try:
                    with transaction.atomic():
                        new_obj.save()
                    created += 1
                    break
                except IntegrityError:
                    continue
            else:
                failed += 1
        if created:
            self.message_user(
                request, f"{created} item(ns) duplicado(s).", messages.SUCCESS
            )
        if failed:
            self.message_user(
                request,
                f"{failed} item(ns) não puderam ser duplicados.",
                messages.WARNING,
            )

    def _get_unique_char_fields(self, model):
        meta = model._meta
        char_types = (django_models.CharField, django_models.TextField)
        fields_by_name = {f.name: f for f in meta.fields}
        unique_fields = set()
        for f in fields_by_name.values():
            if isinstance(f, char_types) and f.unique and not f.primary_key:
                unique_fields.add(f.name)
        for constraint in meta.constraints:
            if isinstance(constraint, django_models.UniqueConstraint):
                for field_name in constraint.fields:
                    f = fields_by_name.get(field_name)
                    if f and isinstance(f, char_types):
                        unique_fields.add(field_name)
        return unique_fields

    actions = [
        "soft_delete_selected",
        "restore_selected",
        "duplicate_selected",
    ]

    def get_queryset(self, request):
        return self.model.everything.all()
