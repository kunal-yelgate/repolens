"""Evidence tracking and confidence estimation."""

from typing import List
from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    category: str
    fact: str
    source_file: str
    line_number: int = 1
    confidence: float = 1.0


class ConfidenceScore(BaseModel):
    value: float  # 0.0 to 1.0
    label: str  # High (>= 0.85), Moderate (0.60 - 0.84), Low (< 0.60)

    @classmethod
    def from_float(cls, val: float) -> "ConfidenceScore":
        val_clamped = max(0.0, min(1.0, val))
        if val_clamped >= 0.85:
            lbl = "High"
        elif val_clamped >= 0.60:
            lbl = "Moderate"
        else:
            lbl = "Low"
        return cls(value=round(val_clamped, 2), label=lbl)
