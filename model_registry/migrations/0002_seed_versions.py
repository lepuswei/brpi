import hashlib
import json

from django.conf import settings
from django.db import migrations
from django.utils import timezone

from model_registry.engine.illustrative_v1 import ILLUSTRATIVE_COEFFICIENTS


def seed_versions(apps, schema_editor):
    QuestionnaireVersion = apps.get_model("model_registry", "QuestionnaireVersion")
    ModelVersion = apps.get_model("model_registry", "ModelVersion")

    QuestionnaireVersion.objects.get_or_create(
        name=settings.BRPI_QUESTIONNAIRE_NAME,
        semantic_version=settings.BRPI_QUESTIONNAIRE_VERSION,
        defaults={
            "status": "frozen",
            "item_definition": {
                "window_days": 7,
                "domains": [
                    "heartburn",
                    "regurgitation",
                    "nocturnal",
                    "postprandial",
                    "supine_bending",
                    "epigastric",
                    "nausea",
                    "context",
                ],
            },
            "frozen_at": timezone.now(),
        },
    )

    coeff = dict(ILLUSTRATIVE_COEFFICIENTS)
    checksum = hashlib.sha256(json.dumps(coeff, sort_keys=True).encode()).hexdigest()
    ModelVersion.objects.get_or_create(
        name=settings.BRPI_MODEL_NAME,
        semantic_version=settings.BRPI_MODEL_VERSION,
        defaults={
            "model_class_path": "model_registry.engine.illustrative_v1.IllustrativeLogisticModelV1",
            "coefficient_json": coeff,
            "predictor_definitions": {
                "HF": "heartburn days 0-7",
                "HI": "heartburn intensity 0-10",
                "RF": "regurgitation days 0-7",
                "RI": "regurgitation intensity 0-10",
                "N": "nocturnal nights 0-7",
                "P": "postprandial association 0/1",
                "S": "supine/bending association 0/1",
                "E": "epigastric-pain days 0-7",
            },
            "action_zone_metadata": {
                "low": "<0.20",
                "indeterminate": "0.20 to <0.80",
                "high": ">=0.80",
                "label_suffix": "demonstration",
            },
            "validation_status": "illustrative_only",
            "clinical_use_permitted": False,
            "checksum": checksum,
            "is_active": True,
            "activated_at": timezone.now(),
        },
    )


def unseed(apps, schema_editor):
    QuestionnaireVersion = apps.get_model("model_registry", "QuestionnaireVersion")
    ModelVersion = apps.get_model("model_registry", "ModelVersion")
    QuestionnaireVersion.objects.filter(
        name=settings.BRPI_QUESTIONNAIRE_NAME,
        semantic_version=settings.BRPI_QUESTIONNAIRE_VERSION,
    ).delete()
    ModelVersion.objects.filter(
        name=settings.BRPI_MODEL_NAME,
        semantic_version=settings.BRPI_MODEL_VERSION,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("model_registry", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_versions, unseed),
    ]
