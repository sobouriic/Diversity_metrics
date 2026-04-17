import os
from typing import List, Dict, Any
import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.diversity_scorer import compute_diversity


_SEMANTIC_SANITY_OK = None


def _env_int(name: str, default: int, min_value: int = 2) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return max(min_value, int(raw))
    except ValueError:
        return default


def _semantic_sanity_check_once() -> bool:
    global _SEMANTIC_SANITY_OK
    if _SEMANTIC_SANITY_OK is not None:
        return _SEMANTIC_SANITY_OK

    try:
        identical_diversity = compute_diversity(["same text", "same text"])
        _SEMANTIC_SANITY_OK = identical_diversity <= 0.1
    except Exception:
        _SEMANTIC_SANITY_OK = False
    return _SEMANTIC_SANITY_OK


def _build_spotcheck_sample(solutions: List[str], sample_size: int) -> List[str]:
    if len(solutions) <= sample_size:
        return solutions

    indices = np.linspace(0, len(solutions) - 1, num=sample_size, dtype=int)
    return [solutions[index] for index in indices]


@dataclass
class ValidationReport:

    valid: bool
    warnings: List[str]
    checks_passed: int
    total_checks: int
    details: Dict[str, Any]


def validate_diversity(
    solutions: List[str],
    computed_score: float,
    context_mission: str = None,
    context_goal: str = None,
) -> ValidationReport:
   
    
    warnings = []
    checks_passed = 0
    total_checks = 4 
    
    details = {
        "score": computed_score,
        "solution_count": len(solutions),
        "checks": {}
    }
    
    # Diversity score MUST be in [0.0, 1.0] and NOT NaN
    if 0.0 <= computed_score <= 1.0 and not np.isnan(computed_score):
        checks_passed += 1
        details["checks"]["range_valid"] = True
    else:
        # Fail: score outside valid range
        warnings.append(f"Diversity score {computed_score} outside [0, 1]")
        details["checks"]["range_valid"] = False
    
    # Score must be a valid number (not NaN, not inf)
    if isinstance(computed_score, (int, float)) and np.isfinite(computed_score):
        checks_passed += 1
        details["checks"]["numeric_valid"] = True
    else:
        # Fail: not a valid number or is infinity
        warnings.append(f"Diversity score {computed_score} is not a valid number")
        details["checks"]["numeric_valid"] = False
    
    # Spot-check numerical pipeline on either full list (small N) or sampled subset (large N).
    spotcheck_size = _env_int("VALIDATION_SPOTCHECK_SIZE", 16)
    spotcheck_tolerance = float(os.getenv("VALIDATION_SPOTCHECK_TOLERANCE", "1e-5"))

    try:
        spotcheck_solutions = _build_spotcheck_sample(solutions, spotcheck_size)
        spotcheck_score = compute_diversity(
            spotcheck_solutions,
            context_mission,
            context_goal,
        )

        if len(spotcheck_solutions) == len(solutions):
            if abs(spotcheck_score - computed_score) <= spotcheck_tolerance:
                checks_passed += 1
                details["checks"]["spot_check"] = True
            else:
                warnings.append(
                    f"Spot-check failed: computed {spotcheck_score}, got {computed_score}"
                )
                details["checks"]["spot_check"] = False
        else:
            if isinstance(spotcheck_score, (int, float)) and np.isfinite(spotcheck_score):
                checks_passed += 1
                details["checks"]["spot_check"] = True
            else:
                warnings.append("Spot-check failed on sampled solutions.")
                details["checks"]["spot_check"] = False
    except Exception as e:
        # Fail: recomputation crashed
        warnings.append(f"Spot-check recomputation failed: {str(e)}")
        details["checks"]["spot_check"] = False
    
    # Run semantic sanity once per process (instead of once per request).
    semantic_valid = _semantic_sanity_check_once()
    if semantic_valid:
        checks_passed += 1
        details["checks"]["semantic_valid"] = True
    else:
        warnings.append("Semantic sanity check failed for identical-solution baseline.")
        details["checks"]["semantic_valid"] = False
   
    valid = checks_passed >= 3
    
    return ValidationReport(
        valid=valid,
        warnings=warnings,
        checks_passed=checks_passed,
        total_checks=total_checks,
        details=details
    )
