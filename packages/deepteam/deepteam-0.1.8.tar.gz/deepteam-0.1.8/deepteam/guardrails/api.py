# This file is kept for compatibility but is no longer needed 
# since deepteam guardrails are fully open-source and local

from typing import Optional, List, Union, Dict
from pydantic import BaseModel

from deepteam.guardrails.types import GuardType


class GuardData(BaseModel):
    """
    Data structure for guard results.
    Used internally by the guardrails system.
    """
    guard: str
    score: float
    reason: str
    safe: bool


class GuardResult(BaseModel):
    """
    Result from guardrails evaluation.
    """
    breached: bool
    guard_verdicts: Dict[str, GuardData]
