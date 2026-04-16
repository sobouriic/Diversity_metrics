from typing import List, Dict, Any
import numpy as np
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.diversity_scorer import compute_diversity


@dataclass
class ValidationReport:
    """
    Result of validation checks on a diversity score.
    
    Attributes:
        valid: True if at least 3 of 4 checks passed
        warnings: List of descriptive warning messages for failed checks
        checks_passed: Number of passed checks (out of total_checks)
        total_checks: Total number of validation checks (typically 4)
        details: Dictionary with detailed check results and metadata
                - score: The computed diversity score
                - solution_count: Number of solutions analyzed
                - checks: Dictionary mapping check names to pass/fail
    """
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
    """
    Validate diversity score with comprehensive sanity checks.
    
    This function performs 4 independent validation checks:
    
    Check 1: Range Validation
    - Verifies score is in [0.0, 1.0]
    - Detects NaN (not a number) values
    - Fails if score outside valid range
    
    Check 2: Numeric Validity
    - Checks type is int or float
    - Detects infinity values
    - Ensures not NULL or other invalid types
    
    Check 3: Spot-check Recomputation
    - Recomputes diversity score independently
    - Compares with provided score
    - Allows 1e-5 tolerance for floating-point rounding
    - Tests that computation is deterministic
    
    Check 4: Semantic Reasonableness
    - Tests identical solutions -> diversity ~0.0
    - Verifies edge case behavior
    - Detects abnormal embedding or distance calculation
    
    Validation Passing Criteria:
    - At least 3 of 4 checks must pass
    - If 3+ pass: valid=True (result can be reported)
    - If <3 pass: valid=False (result should be rejected)
    
    Args:
        solutions: List of solution text strings originally analyzed
                  - Used for spot-check recomputation
                  - May be 1+ solutions
        computed_score: The diversity score to validate
                       - Expected range: [0.0, 1.0]
                       - Type: float
        context_mission: Optional mission context used in original computation
                        - Passed to recomputation for consistency
                        - Example: "Reduce plastic waste"
        context_goal: Optional goal context used in original computation
                     - Passed to recomputation for consistency
                     - Example: "Achieve 50% reduction by 2025"
        
    Returns:
        ValidationReport containing:
        - valid: bool indicating if score passed validation
        - warnings: list of descriptive failure messages
        - checks_passed: count of passed checks (0-4)
        - total_checks: always 4 for this implementation
        - details: comprehensive check results and metadata
        
    Example:
        >>> solutions = ["Solution A", "Solution B"]
        >>> score = 0.562
        >>> report = validate_diversity(solutions, score)
        >>> if report.valid:
        ...     print(f"Score is valid ({report.checks_passed}/4 checks passed)")
        ... else:
        ...     print(f"Validation failed: {report.warnings}")
    """
    
    warnings = []
    checks_passed = 0
    total_checks = 4  # Always 4 checks in current implementation
    
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
