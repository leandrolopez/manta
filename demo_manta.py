
import asyncio
from manta.core.outcomes import OutcomeSpace, Issue
# Note: Ensure your preferences.py has LinearAdditiveUtility implemented!
from manta.core.preferences import LinearAdditiveUtility 
from manta.core.agent import BaseAgent, AgentState, AgentResult
from manta.negotiation.runner import Runner, NegotiationConfig

# --- 1. Define the World ---
space = OutcomeSpace(issues=[
    Issue(name="price", type="continuous", min_value=50, max_value=100),
    Issue(name="service", type="discrete", values=["standard", "premium"])
])

# --- 2. Define the Agents ---
class Buyer(BaseAgent):
    def on_negotiation_start(self, state):
        print(f"[{self.__class__.__name__}] Ready to buy.")

    async def propose(self, state: AgentState) -> AgentResult:
        # Buyer offers Low Price
        return AgentResult(response="offer", proposal={"price": 10, "service": "premium"})

    async def respond(self, state: AgentState) -> AgentResult:
        # Simple logic: If price < 50, accept.
        offer = state.current_offer
        if offer and offer['price'] < 50:
            return AgentResult(response="accept")
        return AgentResult(response="reject")

class Seller(BaseAgent):
    async def propose(self, state: AgentState) -> AgentResult:
        # Seller offers High Price
        return AgentResult(response="offer", proposal={"price": 90, "service": "standard"})

    async def respond(self, state: AgentState) -> AgentResult:
        return AgentResult(response="reject")

# --- 3. Run the Engine ---
async def main():
    config = NegotiationConfig(max_steps=5, time_limit=2.0, outcome_space=space)
    runner = Runner(config=config, agents=[Buyer(), Seller()])
    
    print(">>> Starting Manta Negotiation...")
    result = await runner.run()
    
    print(f"\n>>> Final Result: {result.status}")
    print(f">>> History Length: {len(result.history)}")

if __name__ == "__main__":
    asyncio.run(main())