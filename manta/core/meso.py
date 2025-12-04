from typing import List, Any, Callable, Optional
import random

def generate_meso(
    outcome_space: List[Any],
    utility_function: Callable[[Any], float],
    target_utility: float,
    tolerance: float = 0.05,
    size: int = 3
) -> List[Any]:
    """
    Generate a Multiple Equivalent Simultaneous Offer (MESO).
    
    Args:
        outcome_space: List of all possible outcomes to search from.
        utility_function: Function that maps an outcome to a utility value.
        target_utility: The desired utility level.
        tolerance: The allowed deviation from the target utility.
        size: The number of outcomes to return (k).
        
    Returns:
        A list of 'size' outcomes that have utility within [target - tolerance, target + tolerance].
    """
    
    candidates = []
    
    # 1. Search
    for outcome in outcome_space:
        u = utility_function(outcome)
        if abs(u - target_utility) <= tolerance:
            candidates.append(outcome)
            
    # 2. Selection
    # If we found fewer candidates than requested size, return all of them.
    if len(candidates) <= size:
        return candidates
    
    # Otherwise, select 'size' distinct outcomes.
    # Simple random selection for now.
    return random.sample(candidates, size)
