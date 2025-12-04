
from typing import List, Any, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field, model_validator

# 1. Type Definitions
# An Outcome is just a dictionary: {"price": 100, "delivery": "NextDay"}
Outcome = Dict[str, Any]

# 2. The "Issue" (One dimension of the negotiation)
class Issue(BaseModel):
    name: str
    type: Literal['discrete', 'continuous']
    
    # For Discrete (e.g., Color: Red, Blue)
    values: Optional[List[Any]] = None
    
    # For Continuous (e.g., Price: 10.0 to 100.0)
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    @model_validator(mode='after')
    def check_consistency(self) -> 'Issue':
        if self.type == 'discrete' and not self.values:
            raise ValueError(f"Discrete issue '{self.name}' must have a list of 'values'.")
        if self.type == 'continuous' and (self.min_value is None or self.max_value is None):
            raise ValueError(f"Continuous issue '{self.name}' must have min_value and max_value.")
        return self

# 3. The "Outcome Space" (The Rules of the Game)
class OutcomeSpace(BaseModel):
    issues: List[Issue]

    def get_issue(self, name: str) -> Optional[Issue]:
        for i in self.issues:
            if i.name == name:
                return i
        return None

    def is_valid(self, outcome: Outcome) -> bool:
        """Checks if a bid is valid within the rules."""
        for key, val in outcome.items():
            issue = self.get_issue(key)
            if not issue:
                return False # Unknown issue name
            
            if issue.type == 'discrete':
                if val not in issue.values:
                    return False
            elif issue.type == 'continuous':
                if not (issue.min_value <= val <= issue.max_value):
                    return False
        return True