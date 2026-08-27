from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

from model_registry.engine.base import PredictionResult

# Exact manuscript demonstration coefficients.
ILLUSTRATIVE_COEFFICIENTS: dict[str, float] = {
    "intercept": -6.60,
    "HF": 0.30,
    "HI": 0.20,
    "RF": 0.35,
    "RI": 0.24,
    "HF_HI": 0.045,
    "RF_RI": 0.055,
    "N": 0.18,
    "P": 0.25,
    "S": 0.20,
    "E": -0.10,
}

PAPER_EXAMPLE_INPUTS: dict[str, float | int] = {
    "HF": 5,
    "HI": 6,
    "RF": 4,
    "RI": 5,
    "N": 2,
    "P": 1,
    "S": 1,
    "E": 1,
}

# Prewritten manuscript illustration only — not a calculated interval.
PAPER_EXAMPLE_UNCERTAINTY = (Decimal("0.74"), Decimal("0.94"))

ZONE_LOW = "low demonstration zone"
ZONE_INDETERMINATE = "indeterminate demonstration zone"
ZONE_HIGH = "high-probability demonstration zone"

CONTRIBUTOR_LABELS = {
    "HF": "heartburn frequency",
    "HI": "heartburn intensity",
    "HF_HI": "heartburn frequency–intensity interaction",
    "RF": "regurgitation frequency",
    "RI": "regurgitation intensity",
    "RF_RI": "regurgitation frequency–intensity interaction",
    "N": "nocturnal symptoms",
    "P": "postprandial association",
    "S": "positional (supine/bending) association",
    "E": "epigastric-pain term",
}


def _d(value: float) -> Decimal:
    return Decimal(str(round(value, 10)))


def classify_zone(probability: float) -> str:
    if probability < 0.20:
        return ZONE_LOW
    if probability < 0.80:
        return ZONE_INDETERMINATE
    return ZONE_HIGH


class IllustrativeLogisticModelV1:
    """Manuscript logistic demonstration equation — not clinically validated."""

    name = "IllustrativeLogisticModel"
    version = "1.0.0"
    validation_status = "illustrative_only"
    clinical_use_permitted = False
    training_dataset = None
    calibration_dataset = None

    coefficients = ILLUSTRATIVE_COEFFICIENTS

    def predict(
        self,
        inputs: Mapping[str, float | int | bool],
        *,
        safety_override: bool = False,
        include_paper_uncertainty: bool = False,
    ) -> PredictionResult:
        meta = {
            "validation_status": self.validation_status,
            "clinical_use_permitted": "false",
            "label": "Illustrative—not clinically validated",
        }

        if safety_override:
            return PredictionResult(
                probability=None,
                zone="safety override — no illustrative probability calculated",
                safety_override=True,
                contributors={},
                model_name=self.name,
                model_version=self.version,
                uncertainty_method=None,
                metadata=meta,
            )

        hf = float(inputs["HF"])
        hi = float(inputs["HI"])
        rf = float(inputs["RF"])
        ri = float(inputs["RI"])
        n = float(inputs["N"])
        p = float(inputs["P"])
        s = float(inputs["S"])
        e = float(inputs["E"])

        c = self.coefficients
        terms = {
            "HF": c["HF"] * hf,
            "HI": c["HI"] * hi,
            "HF_HI": c["HF_HI"] * hf * hi,
            "RF": c["RF"] * rf,
            "RI": c["RI"] * ri,
            "RF_RI": c["RF_RI"] * rf * ri,
            "N": c["N"] * n,
            "P": c["P"] * p,
            "S": c["S"] * s,
            "E": c["E"] * e,
        }

        eta = c["intercept"] + sum(terms.values())
        probability = 1.0 / (1.0 + math.exp(-eta))
        zone = classify_zone(probability)

        contributors = {label: _d(value) for label, value in terms.items()}

        unc_lo = unc_hi = unc_method = None
        if include_paper_uncertainty:
            unc_lo, unc_hi = PAPER_EXAMPLE_UNCERTAINTY
            unc_method = "prewritten_manuscript_illustration"

        return PredictionResult(
            probability=_d(probability).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            zone=zone,
            safety_override=False,
            contributors=contributors,
            model_name=self.name,
            model_version=self.version,
            eta=_d(eta).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            uncertainty_lower=unc_lo,
            uncertainty_upper=unc_hi,
            uncertainty_method=unc_method,
            metadata=meta,
        )

    def probability_at(
        self,
        base_inputs: Mapping[str, float | int | bool],
        *,
        hf: float | None = None,
        hi: float | None = None,
        rf: float | None = None,
        ri: float | None = None,
    ) -> float:
        payload = dict(base_inputs)
        if hf is not None:
            payload["HF"] = hf
        if hi is not None:
            payload["HI"] = hi
        if rf is not None:
            payload["RF"] = rf
        if ri is not None:
            payload["RI"] = ri
        result = self.predict(payload)
        assert result.probability is not None
        return float(result.probability)

    def frequency_curve(
        self,
        base_inputs: Mapping[str, float | int | bool],
        *,
        vary: str = "HF",
        values: range | None = None,
    ) -> list[dict[str, float]]:
        values = values or range(0, 8)
        points: list[dict[str, float]] = []
        for v in values:
            kwargs = {vary.lower() if vary in {"HF", "RF"} else vary: float(v)}
            # Map HF/RF explicitly
            if vary == "HF":
                p = self.probability_at(base_inputs, hf=float(v))
            elif vary == "RF":
                p = self.probability_at(base_inputs, rf=float(v))
            else:
                raise ValueError(f"Unsupported curve axis: {vary}")
            points.append({"x": float(v), "y": p})
        return points

    def bivariate_surface(
        self,
        base_inputs: Mapping[str, float | int | bool],
        *,
        freq_key: str = "HF",
        intensity_key: str = "HI",
    ) -> dict:
        xs = list(range(0, 8))
        ys = list(range(0, 11))
        z: list[list[float]] = []
        for intensity in ys:
            row: list[float] = []
            for freq in xs:
                if freq_key == "HF":
                    p = self.probability_at(base_inputs, hf=float(freq), hi=float(intensity))
                else:
                    p = self.probability_at(base_inputs, rf=float(freq), ri=float(intensity))
                row.append(p)
            z.append(row)
        return {"x": xs, "y": ys, "z": z, "freq_key": freq_key, "intensity_key": intensity_key}


def get_active_model() -> IllustrativeLogisticModelV1:
    return IllustrativeLogisticModelV1()


def ranked_contributors(contributors: Mapping[str, Decimal]) -> list[dict]:
    ranked = sorted(contributors.items(), key=lambda item: abs(item[1]), reverse=True)
    return [
        {
            "code": code,
            "label": CONTRIBUTOR_LABELS.get(code, code),
            "value": value,
            "abs_value": abs(value),
        }
        for code, value in ranked
    ]


def explain_top_contributors(contributors: Mapping[str, Decimal], *, top_n: int = 3) -> str:
    ranked = ranked_contributors(contributors)[:top_n]
    if not ranked:
        return (
            "In this illustrative equation, no dominant positive or negative "
            "mathematical contributors were identified."
        )
    positives = [r["label"] for r in ranked if r["value"] > 0]
    if positives:
        joined = ", ".join(positives[:-1]) + (
            f" and {positives[-1]}" if len(positives) > 1 else positives[0]
        )
        return (
            f"In this illustrative equation, {joined} increased the displayed value "
            "most strongly. Contributors are associations within an illustrative "
            "equation, not causes."
        )
    return (
        "In this illustrative equation, negative mathematical terms reduced the "
        "displayed value most strongly. Contributors are associations within an "
        "illustrative equation, not causes."
    )
