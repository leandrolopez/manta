from typing import List, Tuple, Any, Dict

def is_dominated(candidate_utils: Tuple[float, ...], frontier_utils: List[Tuple[float, ...]]) -> bool:
    """
    Check if candidate_utils is dominated by any point in frontier_utils.
    A dominates B if A[i] >= B[i] for all i, and A[i] > B[i] for at least one i.
    """
    for point in frontier_utils:
        # Check if point dominates candidate
        at_least_one_better = False
        all_at_least_equal = True
        
        for p_val, c_val in zip(point, candidate_utils):
            if p_val < c_val:
                all_at_least_equal = False
                break
            if p_val > c_val:
                at_least_one_better = True
        
        if all_at_least_equal and at_least_one_better:
            return True
    return False

def find_pareto_frontier(outcomes: List[Any], utilities: List[Tuple[float, ...]]) -> List[int]:
    """
    Find the indices of outcomes that are on the Pareto Frontier.
    
    Args:
        outcomes: List of outcome objects (not used in comparison, just for indexing if needed, 
                  but here we return indices so it might be redundant, but keeping signature generic).
        utilities: List of utility vectors corresponding to outcomes. 
                   Each tuple contains utilities for all agents for that outcome.
                   
    Returns:
        List of indices of outcomes on the Pareto Frontier.
    """
    # 1. Pre-sort by Social Welfare (sum of utilities) descending
    # Store (original_index, utility_vector, social_welfare)
    indexed_points = []
    for i, utils in enumerate(utilities):
        sw = sum(utils)
        indexed_points.append((i, utils, sw))
    
    # Sort descending by SW
    indexed_points.sort(key=lambda x: x[2], reverse=True)
    
    frontier_indices = []
    frontier_utils = []
    
    # 2. Filtering Loop
    for idx, candidate_utils, _ in indexed_points:
        if not is_dominated(candidate_utils, frontier_utils):
            frontier_indices.append(idx)
            frontier_utils.append(candidate_utils)
            
    return sorted(frontier_indices)
