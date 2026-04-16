from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class Solution(BaseModel):
    """Single solution object."""
    title: str = Field(..., min_length=2, max_length=500)
    description: str = Field(..., min_length=10, max_length=2000)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('description')
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()


class AnalyzeRequest(BaseModel):
    """Request body for manual analysis."""
    solutions: List[Solution] = Field(..., min_items=2, max_items=100)
    mission: Optional[str] = Field(default=None, max_length=500)
    goal: Optional[str] = Field(default=None, max_length=500)
    
    @validator('mission', 'goal', pre=True, always=True)
    def clean_context(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return v.strip() if isinstance(v, str) else v


class ExperimentAnalyzeRequest(BaseModel):
    """Request body for experiment folder analysis."""
    folder_path: str
    condition: int = Field(..., ge=0, le=3)
    domain: str = Field(
        ...,
        pattern=r"(renewable_energy|kyoto_tourism|um6p_university)"
    )


class ValidationInfo(BaseModel):
    """Validation report info."""
    valid: bool
    warnings: List[str] = Field(default_factory=list)
    checks_passed: int
    details: Dict[str, Any] = Field(default_factory=dict)


class SolutionMetrics(BaseModel):
    """Per-solution metrics and metadata."""
    id: str
    title: str
    description: str
    status: str = "valid"


class MetricsResponse(BaseModel):
    """Response with diversity metric."""
    diversity_score: float = Field(..., ge=0.0, le=1.0)
    solutions: List[SolutionMetrics]
    validation_report: ValidationInfo
    metadata: Dict[str, Any] = Field(default_factory=dict)


def validate_solution(title: str, description: str) -> Solution:
    """Validate and parse individual solution."""
    return Solution(title=title, description=description)


def validate_solution_set(solutions: List[Dict[str, str]]) -> List[Solution]:
    """Validate and parse list of solutions."""
    return [Solution(**sol) for sol in solutions]
