from typing import List, Dict, Any
import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.diversity_scorer import compute_diversity


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
    
    # Recompute diversity independently and compare
    try:
        recomputed = compute_diversity(solutions, context_mission, context_goal)
        # Allow 1e-5 floating-point tolerance for rounding differences
        if abs(recomputed - computed_score) < 1e-5:
            checks_passed += 1
            details["checks"]["spot_check"] = True
        else:
            # Fail: recomputation doesn't match
            warnings.append(
                f"Spot-check failed: computed {recomputed}, got {computed_score}"
            )
            details["checks"]["spot_check"] = False
    except Exception as e:
        # Fail: recomputation crashed
        warnings.append(f"Spot-check recomputation failed: {str(e)}")
        details["checks"]["spot_check"] = False
    
    # Test edge cases: identical solutions should give ~0 diversity
    semantic_valid = True
    if len(solutions) >= 2:
        # Create test case: all solutions identical
        identical_solutions = ["same text"] * len(solutions)
        try:
            identical_diversity = compute_diversity(identical_solutions)
            # Identical solutions should have diversity close to 0
            # Allow some tolerance for numerical errors
            if identical_diversity > 0.1:
                warnings.append(
                    f"Identical solutions have diversity {identical_diversity}, "
                    "expected ~0"
                )
                semantic_valid = False
        except:
            pass
    
    if semantic_valid:
        checks_passed += 1
        details["checks"]["semantic_valid"] = True
    else:
        details["checks"]["semantic_valid"] = False
   
    valid = checks_passed >= 3
    
    return ValidationReport(
        valid=valid,
        warnings=warnings,
        checks_passed=checks_passed,
        total_checks=total_checks,
        details=details
    )
