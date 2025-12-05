
from typing import Literal
from pydantic import BaseModel, Field

class ConcessionStrategy(BaseModel):
    """
    Defines the 'Personality' of the negotiator.
    Calculates the Aspiration Level (Target Utility) at any given time.
    """
    # The Personality Type. There are three main types of curves:
    # - Boulware: Tough negotiator
    # - Linear: Soft negotiator
    # - Conceder: Medium negotiator
    style: Literal["boulware", "linear", "conceder"] = "linear"
    
    # The Range
    start_utility: float = 1.0  # Where we start (Dream deal)
    reservation_value: float = 0.5  # Where we walk away (Worst case)
    
    def get_target(self, progress: float) -> float:
        """
        Calculates target utility based on progress (0.0 to 1.0).
        Formula: Target = Start + (End - Start) * (progress ^ beta)
        """
        # Clamp progress to 0-1
        t = max(0.0, min(1.0, progress))
        
        # Determine Beta (The 'Toughness' factor) based on Style
        # High Beta (>1) = Tough (Stays high for long time)
        # Low Beta (<1) = Soft (Drops quickly)
        beta = 1.0
        if self.style == "boulware":
            beta = 5.0 # Very Tough: At 50% time, we only drop 3% of the way
        elif self.style == "conceder":
            beta = 0.2 # Very Soft: At 50% time, we dropped 87% of the way
            
        # The Concession Math
        target = self.start_utility + (self.reservation_value - self.start_utility) * (t ** beta)
        
        return max(target, self.reservation_value)