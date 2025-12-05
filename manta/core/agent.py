from typing import List, Optional, Any, Literal, Union, Dict
from pydantic import BaseModel, Field, ConfigDict

# 1. The State Object
class AgentState(BaseModel):
    """
    Minimal state passed to the agent during the negotiation loop.
    Contains the current step, time, and the opponent's offer.
    """
    step: int
    time: float
    relative_time: float
    current_offer: Optional[Any] = None
    history: List[Any] = Field(default_factory=list)

# 2. The Result Object
class AgentResult(BaseModel):
    """
    Structured result returned by an agent after an action.
    Ensures the Runner receives valid data (e.g., a proposal or a rejection).
    """
    response: Literal["offer", "accept", "reject", "end", "wait"]
    proposal: Optional[Union[Any, List[Any]]] = None # Supports Single Offer or MESO List
    data: Dict[str, Any] = Field(default_factory=dict) # For metadata or debug logs

# 3. The Base Agent
class BaseAgent(BaseModel):
    """
    Abstract Base Class for all Manta agents.
    Inherits from Pydantic BaseModel to allow automatic configuration, 
    serialization (to JSON), and type validation.
    """
    name: str = "Agent"
    
    # CRITICAL CONFIGURATION:
    # 1. arbitrary_types_allowed: Lets you store complex objects (like Utility classes).
    # 2. extra="allow": Lets you add dynamic attributes (like self.utility) in __init__ or hooks.
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    async def propose(self, state: AgentState) -> AgentResult:
        """
        Called when it is the agent's turn to make an offer.
        Must return an AgentResult with response="offer".
        """
        raise NotImplementedError("Agent must implement propose()")

    async def respond(self, state: AgentState) -> AgentResult:
        """
        Called when the agent needs to respond to an incoming offer.
        Must return an AgentResult with 'accept', 'reject', or 'end'.
        """
        raise NotImplementedError("Agent must implement respond()")

    # --- Lifecycle Hooks ---

    def on_negotiation_start(self, state: AgentState) -> None:
        """
        Called once before the negotiation loop begins.
        Use this to initialize utility functions, load data, or set strategies.
        """
        pass

    def on_error(self, error_details: str) -> None:
        """
        Called when an error occurs in the Runner to allow the agent to clean up.
        """
        pass

    def on_negotiation_end(self, state: AgentState) -> None:
        """
        Called once after the negotiation loop ends.
        Use this to save logs or learn from the outcome.
        """
        pass