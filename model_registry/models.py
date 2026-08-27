from django.db import models


class QuestionnaireVersion(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_FROZEN = "frozen"
    STATUS_RETIRED = "retired"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_FROZEN, "Frozen"),
        (STATUS_RETIRED, "Retired"),
    ]

    name = models.CharField(max_length=200)
    semantic_version = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    item_definition = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    frozen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("name", "semantic_version")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} v{self.semantic_version} ({self.status})"

    def freeze(self):
        if self.status == self.STATUS_FROZEN:
            return
        from django.utils import timezone

        self.status = self.STATUS_FROZEN
        self.frozen_at = timezone.now()
        self.save(update_fields=["status", "frozen_at"])


class ModelVersion(models.Model):
    name = models.CharField(max_length=200)
    semantic_version = models.CharField(max_length=32)
    model_class_path = models.CharField(max_length=255)
    coefficient_json = models.JSONField(default=dict)
    predictor_definitions = models.JSONField(default=dict, blank=True)
    action_zone_metadata = models.JSONField(default=dict, blank=True)
    validation_status = models.CharField(max_length=64, default="illustrative_only")
    clinical_use_permitted = models.BooleanField(default=False)
    checksum = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("name", "semantic_version")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} v{self.semantic_version}"

    def save(self, *args, **kwargs):
        # Immutability: refuse coefficient edits on activated/frozen-like rows.
        if self.pk:
            previous = ModelVersion.objects.filter(pk=self.pk).first()
            if previous and previous.activated_at:
                if previous.coefficient_json != self.coefficient_json:
                    raise ValueError(
                        "Cannot edit coefficients of an activated model version; "
                        "create a new semantic version instead."
                    )
                if previous.predictor_definitions != self.predictor_definitions:
                    raise ValueError(
                        "Cannot edit predictor definitions of an activated model version."
                    )
        super().save(*args, **kwargs)


class AuditEvent(models.Model):
    actor_or_session = models.CharField(max_length=64, blank=True)
    event_type = models.CharField(max_length=64)
    object_identifier = models.CharField(max_length=64, blank=True)
    model_version = models.CharField(max_length=64, blank=True)
    questionnaire_version = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.created_at:%Y-%m-%d %H:%M}"
