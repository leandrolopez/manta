import itertools
import random
from typing import List, Callable, Dict, Any, Union, Optional, Literal
from manta.core.outcomes import OutcomeSpace, Outcome
from manta.core.preferences import LinearAdditiveUtility

# Define the utility function type for clean referencing
UtilityFuncType = Callable[[Outcome], float]

# --- 1. THE MAIN ENTRY POINT (STRATEGY SELECTOR) ---

def generate_meso(
    utility_function: UtilityFuncType,
    outcome_space: OutcomeSpace,
    target_utility: float,
    tolerance: float = 0.05,
    max_offers: int = 3,
    max_attempts: int = 5000,
    # The default method is the highly accurate analytical solver
    method: Literal['analytical_solve', 'monte_carlo'] = 'analytical_solve' 
) -> List[Outcome]:
    """
    Generates Multiple Equivalent Simultaneous Offers (MESO) using the specified method.

    Args:
        target_utility: The desired utility score to hit.
        method: 'analytical_solve' (precise/fast) or 'monte_carlo' (flexible/random).
    """
    if method == 'analytical_solve':
        return _analytical_solve(
            utility_function, outcome_space, target_utility, tolerance, max_offers
        )
    else:
        return _monte_carlo_sampling(
            utility_function, outcome_space, target_utility, tolerance, max_offers, max_attempts
        )


# ----------------------------------------------------------------------
# --- 2. THE ANALYTICAL SOLVER (The "Real MESO" / Production Method) ---
# ----------------------------------------------------------------------

def _analytical_solve(
    utility_function: UtilityFuncType,
    outcome_space: OutcomeSpace,
    target_utility: float,
    tolerance: float = 0.005,
    max_offers: int = 3,
) -> List[Outcome]:
    """
    Solves the utility equation algebraically for the price variable for every 
    discrete combination. This is highly precise and deterministic.
    """
    found_offers: List[Outcome] = []
    
    if not isinstance(utility_function, LinearAdditiveUtility):
        # We need the LinearAdditiveUtility structure to access weights and bounds for solving
        print("Falling back to Monte Carlo: Analytical solution requires LinearAdditiveUtility.")
        return _monte_carlo_sampling(utility_function, outcome_space, target_utility)

    # Setup for Price Back-Calculation
    price_issue: Optional[Issue] = None
    discrete_issues = []
    
    for issue in outcome_space.issues:
        if issue.name == 'price' and issue.type == 'continuous':
            price_issue = issue
        else:
            discrete_issues.append((issue.name, issue.values))

    if not price_issue or not price_issue.max_value or not price_issue.min_value:
        return []

    price_min = price_issue.min_value
    price_max = price_issue.max_value
    price_range = price_max - price_min
    price_weight = utility_function.weights.get('price', 0.0)
    
    # Check if price normalization bounds are set in the utility curve
    price_curve = utility_function._curves.get('price')
    if not price_curve or not price_curve.get('max'):
        print("Analytical solve failed: Price normalization bounds missing from Utility curve.")
        return []

    # Max score contributed by price alone (assuming invert=True for buyer)
    U_price_max_contrib = price_weight * 1.0 
    
    # Iterate Over All Discrete Combinations
    discrete_combinations = itertools.product(*(vals for _, vals in discrete_issues))

    for combo in discrete_combinations:
        if len(found_offers) >= max_offers:
            break
        
        # 1. Calculate Utility Contribution from the FIXED (Non-Price) Issues
        partial_outcome: Outcome = {}
        for i, (issue_name, _) in enumerate(discrete_issues):
            partial_outcome[issue_name] = combo[i]

        # Get the maximum possible score for this combo (at P_min)
        temp_outcome = {**partial_outcome, 'price': price_min}
        U_max_score = utility_function.calculate(temp_outcome)
        
        # Contribution from fixed issues (U_fixed) = Total Score at P_min - Price's Max Contribution
        U_fixed = U_max_score - U_price_max_contrib

        # 2. Determine Required Price Utility (V_P(P))
        if price_weight == 0.0: continue
            
        V_P_required = (target_utility - U_fixed) / price_weight
        
        # 3. Reverse-Engineer the Price (P)
        if V_P_required < 0 or V_P_required > 1:
            continue
        
        # P = P_min + (1.0 - V_P_required) * (P_max - P_min) (Standard linear formula for inverted buyer curve)
        required_price = price_min + (1.0 - V_P_required) * price_range
        
        # 4. Validation and Finalization
        if price_min <= required_price <= price_max:
            final_offer = {**partial_outcome, 'price': required_price}
            score_check = utility_function.calculate(final_offer)
            
            # Use tight tolerance for final check
            if abs(score_check - target_utility) <= tolerance:
                found_offers.append(final_offer)
                
    return found_offers


# --------------------------------------------------------------------
# --- 3. THE MONTE CARLO SAMPLER (The Flexible / Testing Method) ---
# --------------------------------------------------------------------

def _monte_carlo_sampling(
    utility_function: UtilityFuncType,
    outcome_space: OutcomeSpace,
    target_utility: float,
    tolerance: float = 0.05,
    max_offers: int = 3,
    max_attempts: int = 5000
) -> List[Outcome]:
    """
    Randomized search for MESO. Useful for non-linear utility problems or quick testing.
    """
    found_offers: List[Outcome] = []
    
    # Analyze the Space to create samplers
    samplers = {}
    for issue in outcome_space.issues:
        if issue.type == 'discrete':
            samplers[issue.name] = lambda i=issue: random.choice(i.values)
        else:
            samplers[issue.name] = lambda i=issue: random.uniform(i.min_value, i.max_value)
            
    issue_names = list(samplers.keys())
    
    # Random Search Loop
    for _ in range(max_attempts):
        if len(found_offers) >= max_offers:
            break
            
        candidate: Outcome = {name: samplers[name]() for name in issue_names}
        
        try:
            score = utility_function(candidate)
        except Exception:
            continue
            
        if abs(score - target_utility) <= tolerance:
            if candidate not in found_offers:
                found_offers.append(candidate)
                
    return found_offers