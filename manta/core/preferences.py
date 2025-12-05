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

    def calculate(self, outcome: Outcome) -> float:
        total_util = 0.0
        
        for issue, value in outcome.items():
            if issue not in self._curves:
                continue
                
            curve = self._curves[issue]
            weight = curve['weight']
            
            # 1. CONTINUOUS LOGIC (You already had this)
            if curve['type'] == 'linear':
                if curve['min'] is not None and curve['max'] is not None:
                    rng = curve['max'] - curve['min']
                    if rng == 0:
                        norm = 1.0
                    else:
                        norm = (float(value) - curve['min']) / rng
                        norm = max(0.0, min(1.0, norm))
                    
                    if curve['invert']:
                        norm = 1.0 - norm
                    total_util += weight * norm

            ### NEW: DISCRETE LOGIC (This fixes the 0.5 score limit)
            elif curve['type'] == 'discrete':
                mapping = curve['mapping']
                # Get score from map, default to 0.0 if unknown value
                val_score = mapping.get(value, 0.0)
                total_util += weight * val_score
                    
        return total_util

    def __call__(self, outcome: Outcome) -> float:
        return self.calculate(outcome)