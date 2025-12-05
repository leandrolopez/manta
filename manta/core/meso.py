import random
from typing import List, Callable, Dict, Any
from manta.core.outcomes import OutcomeSpace, Outcome

def generate_meso(
    utility_function: Callable[[Outcome], float],
    outcome_space: OutcomeSpace,
    target_utility: float,
    tolerance: float = 0.05,
    max_offers: int = 3,
    max_attempts: int = 5000
) -> List[Outcome]:
    """
    Generates Multiple Equivalent Simultaneous Offers (MESO).
    Creates random dictionary outcomes based on the OutcomeSpace rules.
    """
    found_offers: List[Outcome] = []
    
    # 1. Analyze the Space to create search ranges
    # We create a simple sampler for each issue
    samplers = {}
    for issue in outcome_space.issues:
        if issue.type == 'discrete':
            samplers[issue.name] = lambda i=issue: random.choice(i.values)
        else:
            # For continuous, we sample randomly within the range
            samplers[issue.name] = lambda i=issue: random.uniform(i.min_value, i.max_value)
            
    issue_names = list(samplers.keys())
    
    # 2. Random Search Loop
    for _ in range(max_attempts):
        if len(found_offers) >= max_offers:
            break
            
        # Build a random candidate Outcome (Dictionary)
        candidate: Outcome = {}
        for name in issue_names:
            candidate[name] = samplers[name]()
            
        # 3. Check Utility
        try:
            score = utility_function(candidate)
        except Exception:
            continue
            
        # 4. Check if it matches target (Iso-Utility)
        if abs(score - target_utility) <= tolerance:
            # 5. Check Diversity (Avoid exact duplicates)
            # For continuous values, exact match is rare, but good to check
            if candidate not in found_offers:
                found_offers.append(candidate)
                
    return found_offers