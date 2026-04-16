"""
Orchestration layer for computing solution diversity metrics.

This module:
1. Orchestrates the metric computation pipeline
2. Validates input solutions
3. Computes diversity score using embeddings
4. Validates the computed score
5. Structures the response with metadata

Pipeline Flow:
    Solutions (list[Solution])
        ↓
    Convert to text (title + description)
        ↓
    Compute embeddings (transformer model)
        ↓
    Calculate diversity (mean pairwise cosine distance)
        ↓
    Validate score (sanity checks, warnings)
        ↓
    Build MetricsResponse with metadata
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import uuid
sys.path.insert(0, str(Path(__file__).parent.parent))

from metrics.diversity_scorer import compute_diversity
from metrics.validator import validate_diversity
from metrics.io import MetricsResponse, SolutionMetrics, ValidationInfo, Solution


def compute_all_metrics(
    solutions: List[Solution],
    mission: Optional[str] = None,
    goal: Optional[str] = None,
) -> MetricsResponse:
    """
    Compute comprehensive diversity metrics for a set of solutions.
    
    This is the main orchestration function that:
    1. Converts solutions to text format
    2. Computes diversity score using embeddings
    3. Validates the computed score
    4. Generates solution-level metadata
    5. Constructs response with all metrics
    
    Diversity Score Calculation:
    - Uses all-MiniLM-L6-v2 sentence transformer to embed each solution
    - Computes mean pairwise cosine distance between all solutions
    - Score range: 0 (identical solutions) to 1 (completely different)
    - Formula: mean(cosine_distance(embedding_i, embedding_j)) for all i,j pairs
    
    Validation:
    - Checks score is in valid range [0, 1]
    - Detects NaN or infinity values
    - Validates against known issue patterns
    - Generates warnings for edge cases (very low diversity, etc.)
    
    Args:
        solutions: List of Solution objects with title and description fields
        mission: Optional mission/context field for relevance scoring (future use)
        goal: Optional goal/context field for novelty scoring (future use)
        
    Returns:
        MetricsResponse object containing:
        - diversity_score: float between 0 and 1
        - solutions: List of SolutionMetrics with IDs and status
        - validation_report: ValidationInfo with checks and warnings
        - metadata: Dict with model info and input characteristics
        
    Raises:
        ValueError: If solution format is invalid, computation fails, or validation fails
        
    Example:
        >>> from metrics.io import Solution
        >>> solutions = [
        ...     Solution(title="Solution A", description="Details about approach A"),
        ...     Solution(title="Solution B", description="Details about approach B")
        ... ]
        >>> response = compute_all_metrics(solutions, mission="Reduce waste")
        >>> print(f"Diversity: {response.diversity_score:.3f}")
        Diversity: 0.562
    """
    
    # Step 1: Convert solutions to text format (combine title and description)
    # This provides full context for embedding generation
    solution_texts = [
        f"{s.title}. {s.description}" for s in solutions
    ]
    
    # Step 2: Compute diversity score
    # Returns value in [0, 1] representing average pairwise difference
    diversity_score = compute_diversity(solution_texts, mission, goal)
    
    # Step 3: Validate the computed diversity score
    # Checks for edge cases, NaN values, and generates warnings
    validation = validate_diversity(
        solution_texts,
        diversity_score,
        mission,
        goal
    )
    
    # Step 4: Build solution-level metrics
    # Assigns unique IDs and status to each solution
    solution_metrics = []
    for i, solution in enumerate(solutions):
        solution_metrics.append(
            SolutionMetrics(
                id=f"sol_{i+1}",
                title=solution.title,
                description=solution.description,
                status="valid"
            )
        )
    
    # Step 5: Build comprehensive response object
    return MetricsResponse(
        diversity_score=diversity_score,
        solutions=solution_metrics,
        validation_report=ValidationInfo(
            valid=validation.valid,
            warnings=validation.warnings,
            checks_passed=validation.checks_passed,
            details={
                "diversity_validation": validation.details,
                "total_solutions": len(solutions),
            }
        ),
        metadata={
            "embeddings_model": "all-MiniLM-L6-v2",
            "embeddings_dimension": 384,
            "total_solutions": len(solutions),
            "solutions_count": len(solutions),
            "context_provided": {
                "mission": mission is not None,
                "goal": goal is not None,
            }
        }
    )
