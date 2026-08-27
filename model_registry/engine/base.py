from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping, Protocol


@dataclass(frozen=True)
class PredictionResult:
    probability: Decimal | None
    zone: str
    safety_override: bool
    contributors: Mapping[str, Decimal]
    model_name: str
    model_version: str
    eta: Decimal | None = None
    uncertainty_lower: Decimal | None = None
    uncertainty_upper: Decimal | None = None
    uncertainty_method: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


class BRPIModel(Protocol):
    name: str
    version: str

    def predict(self, inputs: Mapping[str, float | int | bool]) -> PredictionResult:
        ...
