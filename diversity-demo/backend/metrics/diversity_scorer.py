from typing import List, Optional
import numpy as np
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.embeddings import embed_texts, pairwise_distances

logger = logging.getLogger(__name__)


def compute_diversity(
    solutions: List[str],
    context_mission: Optional[str] = None,
    context_goal: Optional[str] = None,
) -> float:
    """
    Compute diversity score as mean pairwise cosine distance.
    
    Formula:
        diversity = mean([distance(solution_i, solution_j) for all i < j])
    
    Where distance is cosine distance in [0, 1]:
    - 0.0 = solutions are identical
    - 1.0 = solutions are maximally different
    
    Args:
        solutions: List of solution description strings (N >= 2)
        context_mission: Optional mission context to prepend for grounding
        context_goal: Optional goal context to prepend for grounding
        
    Returns:
        Diversity score in [0.0, 1.0]
        
    Raises:
        ValueError: If fewer than 2 solutions provided
        TypeError: If solutions not a list of strings
    """
    
    if not isinstance(solutions, list) or len(solutions) < 1:
        raise ValueError(f"Need at least 1 solution, got {len(solutions)}")
    
    if not all(isinstance(s, str) for s in solutions):
        raise TypeError("All solutions must be strings")
    
    if len(solutions) == 1:
        logger.info("Only 1 solution provided - diversity score set to 0.5 by default")
        return 0.5
    
    enriched_solutions = solutions.copy()
    if context_mission or context_goal:
        context_prefix = ""
        if context_mission:
            context_prefix += f"{context_mission}. "
        if context_goal:
            context_prefix += f"{context_goal}. "
        
        enriched_solutions = [
            context_prefix + sol for sol in solutions
        ]
    
    embeddings = embed_texts(enriched_solutions)
    distances = pairwise_distances(embeddings)
    
    n = len(solutions)
    upper_triangle_indices = np.triu_indices(n, k=1)
    diversity_score = float(np.mean(distances[upper_triangle_indices]))
    diversity_score = max(0.0, min(1.0, diversity_score))
    
    return diversity_score
