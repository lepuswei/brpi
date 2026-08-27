from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from model_registry.engine import PAPER_EXAMPLE_INPUTS, get_active_model
from model_registry.engine.illustrative_v1 import (
    ZONE_HIGH,
    ZONE_INDETERMINATE,
    ZONE_LOW,
    classify_zone,
)
from model_registry.models import ModelVersion
from questionnaire.forms import SafetyScreenForm, SymptomQuestionnaireForm


class IllustrativeModelTests(TestCase):
    def setUp(self):
        self.model = get_active_model()

    def test_paper_example_calculation(self):
        result = self.model.predict(PAPER_EXAMPLE_INPUTS, include_paper_uncertainty=True)
        self.assertFalse(result.safety_override)
        self.assertEqual(result.eta, Decimal("1.86"))
        self.assertEqual(result.probability, Decimal("0.8653"))
        self.assertEqual(f"{float(result.probability):.2f}", "0.87")
        self.assertEqual(result.zone, ZONE_HIGH)
        self.assertEqual(result.uncertainty_lower, Decimal("0.74"))
        self.assertEqual(result.uncertainty_upper, Decimal("0.94"))
        self.assertEqual(result.uncertainty_method, "prewritten_manuscript_illustration")

    def test_no_uncertainty_for_interactive(self):
        result = self.model.predict(PAPER_EXAMPLE_INPUTS, include_paper_uncertainty=False)
        self.assertIsNone(result.uncertainty_lower)
        self.assertIsNone(result.uncertainty_upper)
        self.assertIsNone(result.uncertainty_method)

    def test_safety_override_blocks_prediction(self):
        result = self.model.predict(PAPER_EXAMPLE_INPUTS, safety_override=True)
        self.assertTrue(result.safety_override)
        self.assertIsNone(result.probability)
        self.assertEqual(result.contributors, {})

    def test_zone_boundaries(self):
        self.assertEqual(classify_zone(0.199), ZONE_LOW)
        self.assertEqual(classify_zone(0.20), ZONE_INDETERMINATE)
        self.assertEqual(classify_zone(0.799), ZONE_INDETERMINATE)
        self.assertEqual(classify_zone(0.80), ZONE_HIGH)

    def test_contributors_stable(self):
        result = self.model.predict(PAPER_EXAMPLE_INPUTS)
        self.assertIn("RF", result.contributors)
        self.assertEqual(result.contributors["HF"], Decimal("1.5"))
        self.assertEqual(result.contributors["HF_HI"], Decimal("1.35"))

    def test_frequency_curve_length(self):
        curve = self.model.frequency_curve(PAPER_EXAMPLE_INPUTS, vary="HF")
        self.assertEqual(len(curve), 8)
        self.assertEqual(curve[5]["x"], 5.0)


class FormValidationTests(TestCase):
    def test_symptom_ranges(self):
        form = SymptomQuestionnaireForm(
            data={
                "heartburn_days": 8,
                "heartburn_intensity": 6,
                "regurgitation_days": 4,
                "regurgitation_intensity": 5,
                "nocturnal_nights": 2,
                "postprandial": "most",
                "supine_bending": "often",
                "epigastric_days": 1,
                "epigastric_intensity": 3,
                "nausea_days": 0,
                "nausea_intensity": 0,
                "response_certainty": 80,
                "ppi_use": "no",
                "prior_gerd_evidence": "uncertain",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("heartburn_days", form.errors)

    def test_safety_any_positive(self):
        payload = {key: "no" for key, _ in SafetyScreenForm().fields.items() if key != "comment"}
        payload["dysphagia"] = "yes"
        form = SafetyScreenForm(data=payload)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.any_positive())


class ModelVersionImmutabilityTests(TestCase):
    def test_cannot_edit_coefficients_after_activation(self):
        from django.utils import timezone

        mv = ModelVersion.objects.create(
            name="IllustrativeLogisticModel",
            semantic_version="1.0.0-test",
            model_class_path="model_registry.engine.illustrative_v1.IllustrativeLogisticModelV1",
            coefficient_json={"intercept": -6.6},
            validation_status="illustrative_only",
            clinical_use_permitted=False,
            is_active=True,
            activated_at=timezone.now(),
            checksum="abc",
        )
        mv.coefficient_json = {"intercept": -6.61}
        with self.assertRaises(ValueError):
            mv.save()


class WorkflowIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _consent(self):
        return self.client.post(
            reverse("assessment:consent"),
            {
                "age_confirmed": "on",
                "not_urgent_care": "on",
                "disclaimer_acknowledged": "on",
            },
        )

    def _safety_all_no(self):
        payload = {
            "dysphagia": "no",
            "odynophagia": "no",
            "gi_bleeding": "no",
            "weight_loss": "no",
            "persistent_vomiting": "no",
            "anemia": "no",
            "mass": "no",
            "chest_pain": "no",
            "comment": "",
        }
        return self.client.post(reverse("assessment:safety"), payload)

    def test_paper_example_workflow(self):
        start = self.client.post(reverse("assessment:start"), {"mode": "paper_example"})
        self.assertEqual(start.status_code, 302)
        self.assertEqual(self._consent().status_code, 302)
        self.assertEqual(self._safety_all_no().status_code, 302)

        q = self.client.get(reverse("assessment:questionnaire"))
        self.assertEqual(q.status_code, 200)

        from questionnaire.constants import PAPER_EXAMPLE_SYMPTOMS

        post = self.client.post(reverse("assessment:questionnaire"), PAPER_EXAMPLE_SYMPTOMS)
        self.assertEqual(post.status_code, 302)

        review = self.client.get(reverse("assessment:review"))
        self.assertEqual(review.status_code, 200)

        calc = self.client.post(reverse("assessment:review"), {"action": "calculate"})
        self.assertEqual(calc.status_code, 302)

        report = self.client.get(reverse("reports:report"))
        self.assertEqual(report.status_code, 200)
        self.assertContains(report, "0.87")
        self.assertContains(report, "high-probability demonstration zone")
        self.assertContains(report, "IllustrativeLogisticModel")

    def test_safety_override_workflow(self):
        self.client.post(reverse("assessment:start"), {"mode": "interactive"})
        self._consent()
        payload = {
            "dysphagia": "yes",
            "odynophagia": "no",
            "gi_bleeding": "no",
            "weight_loss": "no",
            "persistent_vomiting": "no",
            "anemia": "no",
            "mass": "no",
            "chest_pain": "no",
        }
        resp = self.client.post(reverse("assessment:safety"), payload)
        self.assertEqual(resp.status_code, 302)
        report = self.client.get(reverse("reports:report"))
        self.assertEqual(report.status_code, 200)
        self.assertContains(report, "Safety override active")
        self.assertNotContains(report, "Patient-specific heartburn frequency curve")

    def test_landing_page(self):
        resp = self.client.get(reverse("core:landing"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Research prototype")

    def test_reset_clears_session_and_returns_home(self):
        self.client.post(reverse("assessment:start"), {"mode": "interactive"})
        self.assertIsNotNone(self.client.session.get("brpi_assessment"))
        resp = self.client.post(reverse("assessment:reset"))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("core:landing"))
        self.assertIsNone(self.client.session.get("brpi_assessment"))
