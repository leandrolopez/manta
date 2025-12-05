import time
import logging
import asyncio
from typing import List, Optional, Any, Literal
from pydantic import BaseModel, Field

# Add OutcomeSpace here so the Config knows what it is
from manta.core.outcomes import OutcomeSpace, Outcome
from manta.core.agent import BaseAgent, AgentState, AgentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NegotiationConfig(BaseModel):
    max_steps: Optional[int] = None
    time_limit: Optional[float] = None
    outcome_space: OutcomeSpace

class NegotiationState(BaseModel):
    running: bool = False
    step: int = 0
    start_time: float = 0.0
    current_proposer_id: str = ""
    current_offer: Optional[Any] = None
    history: List[dict] = []
    status: Literal["ongoing", "success", "timedout", "broken"] = "ongoing"

class Runner(BaseModel):
    config: NegotiationConfig
    agents: List[BaseAgent]
    state: NegotiationState = Field(default_factory=NegotiationState)
    
    class Config:
        arbitrary_types_allowed = True

    def _get_agent_state(self) -> AgentState:
        now = time.time()
        relative_time = 0.0
        if self.config.time_limit and self.config.time_limit > 0:
            relative_time = (now - self.state.start_time) / self.config.time_limit
        
        return AgentState(
            step=self.state.step,
            time=now,
            relative_time=relative_time,
            current_offer=self.state.current_offer,
            history=self.state.history
        )

    async def run(self):
        """Execute the negotiation simulation loop."""
        self.state.running = True
        self.state.start_time = time.time()
        self.state.step = 0
        self.state.status = "ongoing"
        
        # Initialize agents
        for agent in self.agents:
            try:
                agent.on_negotiation_start(self._get_agent_state())
            except Exception as e:
                logger.error(f"Error initializing agent {agent.name}: {e}")
                self.state.status = "broken"
                return self.state # Return state immediately on crash

        current_proposer_idx = 0
        
        while self.state.status == "ongoing":
            # 1. Check Deadlines
            if self.config.max_steps is not None and self.state.step >= self.config.max_steps:
                self.state.status = "timedout"
                break
            
            if self.config.time_limit is not None:
                elapsed = time.time() - self.state.start_time
                if elapsed >= self.config.time_limit:
                    self.state.status = "timedout"
                    break

            # 2. Determine Turn
            proposer = self.agents[current_proposer_idx]
            responder = self.agents[(current_proposer_idx + 1) % len(self.agents)]
            self.state.current_proposer_id = proposer.name

            # 3. Action - Propose
            try:
                # FIXED: We await the async method
                proposal_result = await proposer.propose(self._get_agent_state())
                
                # CRITICAL FIX: Check if agent explicitly wants to end
                if proposal_result.response == "end":
                    logger.info(f"Agent {proposer.name} decided to end the negotiation.")
                    self.state.status = "broken"
                    break

                proposal = proposal_result.proposal
            except Exception as e:
                logger.error(f"Agent {proposer.name} crashed during propose: {e}")
                self.state.status = "broken"
                break

            # 4. Validation
            if proposal is None:
                # FIXED: Do NOT continue if proposal is None. This caused the crash.
                logger.warning(f"Agent {proposer.name} made no proposal (None). Stopping.")
                self.state.status = "broken"
                break
            
            # 5. Action - Respond
            
            # Let's update the state temporarily for the responder call
            temp_state = self._get_agent_state()
            temp_state.current_offer = proposal
            
            try:
                # FIXED: We await the async method
                response_result = await responder.respond(temp_state)
                response = response_result.response
            except Exception as e:
                logger.error(f"Agent {responder.name} crashed during respond: {e}")
                self.state.status = "broken"
                break

            # 6. Process Response
            if response == "accept":
                self.state.status = "success"
                self.state.current_offer = proposal # Final agreement
                # Log the final accept
                self.state.history.append({
                    "step": self.state.step,
                    "proposer": proposer.name,
                    "proposal": proposal,
                    "responder": responder.name,
                    "response": response
                })
                break
            elif response == "reject":
                self.state.current_offer = proposal # Update current offer on table
            elif response == "end":
                self.state.status = "broken"
                break
            
            # 7. Update State
            self.state.history.append({
                "step": self.state.step,
                "proposer": proposer.name,
                "proposal": proposal,
                "responder": responder.name,
                "response": response
            })
            
            self.state.step += 1
            # The Modulo operator (%) enforces the Alternating turn
            current_proposer_idx = (current_proposer_idx + 1) % len(self.agents)
            
            # Small sleep to yield control in async loop
            await asyncio.sleep(0.01)

        # Cleanup
        for agent in self.agents:
            try:
                agent.on_negotiation_end(self._get_agent_state())
            except Exception as e:
                logger.error(f"Error finalizing agent {agent.name}: {e}")

        return self.state