from typing import Dict, Any, Optional
from pydantic import Field, model_validator

# Manta Imports
from manta.core.agent import BaseAgent, AgentState, AgentResult
from manta.core.outcomes import OutcomeSpace
from manta.core.preferences import LinearAdditiveUtility
from manta.core.strategy import ConcessionStrategy
from manta.core.meso import generate_meso

class StandardAgent(BaseAgent):
    """
    The Universal Negotiator.
    Configured entirely via init arguments, no subclassing required.
    """
    # 1. Configuration (The "DNA")
    role: str = "buyer" # 'buyer' or 'seller'
    weights: Dict[str, float]
    outcome_space: OutcomeSpace
    
    # 2. Strategy Config
    personality: str = "linear" # boulware, linear, conceder
    aspiration_start: float = 0.95
    reservation_val: float = 0.50
    
    # 3. Internal State (The "Brain")
    _utility: Optional[LinearAdditiveUtility] = None
    _strategy: Optional[ConcessionStrategy] = None

    def on_negotiation_start(self, state: AgentState):
        # A. Build the Utility Function
        self._utility = LinearAdditiveUtility(
            weights=self.weights,
            outcome_space=self.outcome_space
        )
        
        # B. Setup Curves automatically based on Role
        # Buyers want low price, Sellers want high price.
        for issue, weight in self.weights.items():
            if issue == "price":
                # If I am buyer, invert price (lower is better).
                is_inverted = (self.role == "buyer")
                self._utility.add_curve(issue, weight, invert=is_inverted)
            else:
                # For non-price issues, we assume default mapping or manual config later.
                # For MVP: Assume Higher = Better (e.g. Service Levels: 1=Std, 2=Prem, 3=Ent)
                # In production, you'd pass explicit curve configs.
                pass

        # C. Build the Concession Strategy
        self._strategy = ConcessionStrategy(
            style=self.personality,
            start_utility=self.aspiration_start,
            reservation_value=self.reservation_val
        )
        print(f"[{self.name}] Initialized as {self.role.upper()} ({self.personality})")

    async def propose(self, state: AgentState) -> AgentResult:
        # 1. Calculate Target
        max_steps = 10 # Ideally passed in config
        progress = state.step / max_steps
        target = self._strategy.get_target(progress)
        
        print(f"[{self.name}] Target U: {target:.2f}")
        
        # 2. Generate Offer
        offers = generate_meso(self._utility, self.outcome_space, target, tolerance=0.06, max_offers=3)
        
        if not offers:
            # Panic Fallback (Should be configurable)
            return AgentResult(response="end")
            
        return AgentResult(response="offer", proposal=offers)

    async def respond(self, state: AgentState) -> AgentResult:
        offer = state.current_offer
        if isinstance(offer, list): offer = offer[0] # Simplification

        score = self._utility.calculate(offer)
        
        # HACK: Manual bonus for discrete items since simple LinearUtility needs upgrades
        # In full production, this logic moves into ValueFunctions
        if 'service' in offer:
            if offer['service'] == 'premium': score += 0.1
            if offer['service'] == 'enterprise': score += 0.2
            
        print(f"[{self.name}] Assessing offer: Score {score:.2f}")
        
        if score >= self._strategy.reservation_value:
            return AgentResult(response="accept")
        
        return AgentResult(response="reject")