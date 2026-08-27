from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.utils import timezone

from model_registry.engine import PAPER_EXAMPLE_INPUTS, get_active_model
from model_registry.engine.illustrative_v1 import explain_top_contributors, ranked_contributors
from questionnaire.constants import PAPER_EXAMPLE_SYMPTOMS, SAFETY_ITEMS

SESSION_KEY = "brpi_assessment"


def new_session_code() -> str:
    return uuid.uuid4().hex[:12].upper()


def get_assessment(session) -> dict[str, Any] | None:
    return session.get(SESSION_KEY)


def clear_assessment(session) -> None:
    if SESSION_KEY in session:
        del session[SESSION_KEY]
        session.modified = True


def start_assessment(session, *, mode: str) -> dict[str, Any]:
    data = {
        "session_code": new_session_code(),
        "mode": mode,  # paper_example | interactive
        "started_at": timezone.now().isoformat(),
        "completed_at": None,
        "disclaimer_acknowledged": False,
        "consent": {},
        "safety": {},
        "safety_override": False,
        "symptoms": {},
        "model_inputs": {},
        "result": None,
        "questionnaire_name": settings.BRPI_QUESTIONNAIRE_NAME,
        "questionnaire_version": settings.BRPI_QUESTIONNAIRE_VERSION,
        "model_name": settings.BRPI_MODEL_NAME,
        "model_version": settings.BRPI_MODEL_VERSION,
        "step": "consent",
    }
    if mode == "paper_example":
        data["symptoms"] = dict(PAPER_EXAMPLE_SYMPTOMS)
        data["model_inputs"] = dict(PAPER_EXAMPLE_INPUTS)
    session[SESSION_KEY] = data
    session.modified = True
    return data


def save_assessment(session, data: dict[str, Any]) -> None:
    session[SESSION_KEY] = data
    session.modified = True


def compute_result(data: dict[str, Any]) -> dict[str, Any]:
    model = get_active_model()
    safety_override = bool(data.get("safety_override"))
    include_paper_uncertainty = data.get("mode") == "paper_example" and not safety_override

    prediction = model.predict(
        data.get("model_inputs") or {},
        safety_override=safety_override,
        include_paper_uncertainty=include_paper_uncertainty,
    )

    result: dict[str, Any] = {
        "safety_override": prediction.safety_override,
        "probability": float(prediction.probability) if prediction.probability is not None else None,
        "probability_display": (
            f"{float(prediction.probability):.2f}" if prediction.probability is not None else None
        ),
        "eta": float(prediction.eta) if prediction.eta is not None else None,
        "zone": prediction.zone,
        "contributors": {k: float(v) for k, v in prediction.contributors.items()},
        "ranked_contributors": [
            {
                "code": r["code"],
                "label": r["label"],
                "value": float(r["value"]),
                "abs_value": float(r["abs_value"]),
            }
            for r in ranked_contributors(prediction.contributors)
        ],
        "explanation": explain_top_contributors(prediction.contributors),
        "uncertainty_lower": (
            float(prediction.uncertainty_lower) if prediction.uncertainty_lower is not None else None
        ),
        "uncertainty_upper": (
            float(prediction.uncertainty_upper) if prediction.uncertainty_upper is not None else None
        ),
        "uncertainty_method": prediction.uncertainty_method,
        "model_name": prediction.model_name,
        "model_version": prediction.model_version,
        "metadata": dict(prediction.metadata),
        "generated_at": timezone.now().isoformat(),
    }

    if not safety_override and data.get("model_inputs"):
        result["heartburn_curve"] = model.frequency_curve(data["model_inputs"], vary="HF")
        result["regurgitation_curve"] = model.frequency_curve(data["model_inputs"], vary="RF")
        result["bivariate_surface"] = model.bivariate_surface(data["model_inputs"])

    return result


def safety_summary(safety: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for key, label in SAFETY_ITEMS:
        rows.append(
            {
                "key": key,
                "label": label,
                "value": safety.get(key, "—"),
            }
        )
    return rows


SYMPTOM_LABELS = {
    "heartburn_days": "Heartburn days",
    "heartburn_episodes": "Heartburn episodes",
    "heartburn_intensity": "Heartburn intensity",
    "regurgitation_days": "Regurgitation days",
    "regurgitation_episodes": "Regurgitation episodes",
    "regurgitation_intensity": "Regurgitation intensity",
    "nocturnal_nights": "Nocturnal nights",
    "postprandial": "Postprandial association",
    "supine_bending": "Supine/bending association",
    "epigastric_days": "Epigastric pain days",
    "epigastric_intensity": "Epigastric pain intensity",
    "nausea_days": "Nausea days",
    "nausea_intensity": "Nausea intensity",
    "response_certainty": "Response certainty (%)",
    "ppi_use": "PPI / acid-blocker use",
    "ppi_details": "PPI details",
    "prior_gerd_evidence": "Prior GERD evidence",
    "bmi": "BMI",
    "pregnancy": "Pregnancy",
    "major_comorbidity": "Major comorbidity notes",
}


def symptom_summary(symptoms: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"key": key, "label": SYMPTOM_LABELS.get(key, key), "value": value}
        for key, value in symptoms.items()
    ]
