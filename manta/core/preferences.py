from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, PrivateAttr
from manta.core.outcomes import OutcomeSpace, Outcome

class LinearAdditiveUtility(BaseModel):
    weights: Dict[str, float]
    outcome_space: Optional[OutcomeSpace] = None 
    
    _curves: Dict[str, Any] = PrivateAttr(default_factory=dict)

    def add_curve(self, issue: str, weight: float, min_val: float = None, max_val: float = None, invert: bool = False):
        """Define a continuous curve (Price)."""
        if self.outcome_space and (min_val is None or max_val is None):
            issue_obj = self.outcome_space.get_issue(issue)
            if issue_obj and issue_obj.type == 'continuous':
                min_val = issue_obj.min_value
                max_val = issue_obj.max_value

        self._curves[issue] = {
            "type": "linear",
            "weight": weight,
            "min": min_val,
            "max": max_val,
            "invert": invert
        }

    ### NEW: Method to add discrete mappings (Strings -> Score)
    def add_discrete(self, issue: str, weight: float, mapping: Dict[str, float]):
        """Define a discrete mapping (Service: Premium -> 1.0)."""
        self._curves[issue] = {
            "type": "discrete",
            "weight": weight,
            "mapping": mapping
        }

    # INSIDE CLASS LinearAdditiveUtility:

    def calculate(self, outcome: Outcome) -> float:
        total_util = 0.0
        
        # Determine the effective weight for non-continuous issues
        w_service = self.weights.get('service', 0.0)
        w_duration = self.weights.get('duration', 0.0)
        
        for issue, value in outcome.items():
            if issue not in self._curves and issue not in self.weights:
                continue
                
            curve = self._curves.get(issue)
            weight = self.weights.get(issue, 0.0)
            
            # --- CONTINUOUS LOGIC (PRICE) ---
            if curve and curve.get('type') == 'linear':
                # (Keep existing calculation for min/max/invert here)
                rng = curve['max'] - curve['min']
                if rng == 0:
                    norm = 1.0
                else:
                    norm = (float(value) - curve['min']) / rng
                    norm = max(0.0, min(1.0, norm))
                
                if curve['invert']:
                    norm = 1.0 - norm
                
                total_util += weight * norm
            
            # --- DISCRETE LOGIC (SERVICE, DURATION, etc.) ---
            # This logic must handle the string-to-value mapping internally
            elif issue == 'service' or issue == 'duration':
                # Note: This is simplified based on your demo's assumed utility (Best=1.0)
                score_map = {
                    'enterprise': 1.0, 'premium': 0.5, 'standard': 0.0, # Service
                    '3_years': 1.0, '1_year': 0.0                      # Duration
                }
                
                # Check the exact value and get score contribution
                norm = score_map.get(value, 0.0)
                total_util += weight * norm
            
        return total_util

    def __call__(self, outcome: Outcome) -> float:
        return self.calculate(outcome)