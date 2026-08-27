"""Versioned BRPI calculation engines (Django-independent)."""

from model_registry.engine.base import BRPIModel, PredictionResult
from model_registry.engine.illustrative_v1 import (
    ILLUSTRATIVE_COEFFICIENTS,
    PAPER_EXAMPLE_INPUTS,
    IllustrativeLogisticModelV1,
    get_active_model,
)

__all__ = [
    "BRPIModel",
    "PredictionResult",
    "IllustrativeLogisticModelV1",
    "ILLUSTRATIVE_COEFFICIENTS",
    "PAPER_EXAMPLE_INPUTS",
    "get_active_model",
]
