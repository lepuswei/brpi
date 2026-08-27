from django.contrib import admin

from model_registry.models import AuditEvent, ModelVersion, QuestionnaireVersion


@admin.register(QuestionnaireVersion)
class QuestionnaireVersionAdmin(admin.ModelAdmin):
    list_display = ("name", "semantic_version", "status", "created_at", "frozen_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "frozen_at")


@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "semantic_version",
        "validation_status",
        "clinical_use_permitted",
        "is_active",
        "activated_at",
    )
    list_filter = ("validation_status", "is_active", "clinical_use_permitted")
    readonly_fields = ("created_at", "activated_at", "checksum")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "actor_or_session", "object_identifier", "created_at")
    list_filter = ("event_type",)
    readonly_fields = ("created_at",)
