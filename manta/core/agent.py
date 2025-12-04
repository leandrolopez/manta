from abc import ABC, abstractmethod
from typing import Union, List, Any, Optional
from pydantic import BaseModel

class AgentState(BaseModel):
    """Minimal state passed to the agent."""
    step: int
    time: float
    relative_time: float
    current_offer: Union[Any, None] # The offer on the table (Outcome)
    history: List[Any] # Simplified history

class AgentResult(BaseModel):
    """Result returned by an agent action."""
    response: str # "accept", "reject", "end", "wait"
    proposal: Union[Any, List[Any], None] = None # Outcome or List[Outcome] (MESO)
    data: dict = {}

class BaseAgent(ABC):
    """Abstract Base Class for all Manta agents."""

    def __init__(self, name: str = "Agent"):
        self.name = name

    @abstractmethod
    def propose(self, state: AgentState) -> AgentResult:
        """
        Called when it is the agent's turn to make an offer.
        Returns a proposal (or list of proposals).
        """
        pass

    @abstractmethod
    def respond(self, state: AgentState) -> AgentResult:
        """
        Called when the agent needs to respond to an incoming offer (state.current_offer).
        Returns 'accept', 'reject' (with optional counter-proposal), or 'end'.
        """
        pass

    def on_negotiation_start(self, state: AgentState) -> None:
        """Called when the negotiation starts."""
        pass

    def on_error(self, error_details: str) -> None:
        """Called when an error occurs."""
        pass

    def on_negotiation_end(self, state: AgentState) -> None:
        """Called when the negotiation ends."""
        pass
