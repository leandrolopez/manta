import asyncio
from typing import List, Union

# Manta Core Imports
from manta.core.outcomes import OutcomeSpace, Issue
from manta.core.preferences import LinearAdditiveUtility
from manta.core.agent import BaseAgent, AgentState, AgentResult
from manta.core.meso import generate_meso 
from manta.negotiation.runner import Runner, NegotiationConfig

# --- 1. CONFIGURATION ---
print("\n--- MANTA NEGOTIATION SETUP ---")

# A. The Scenario
budget = float(input("Buyer Max Budget (e.g. 200): ") or 200)
ask = float(input("Seller Asking Price (e.g. 150): ") or 150)

# B. The Variables (Weights)
print("\n[Buyer Priorities] - Total should sum to roughly 1.0")
w_price = float(input("Weight: Price (Default 0.5): ") or 0.5)
w_service = float(input("Weight: Service (Default 0.3): ") or 0.3)
w_duration = float(input("Weight: Duration (Default 0.2): ") or 0.2)

# C. The Strategy
mode = input("\nChoose Strategy (simple/meso) [default: meso]: ").lower() or "meso"
initiator = input("Who starts? (buyer/seller) [default: buyer]: ").lower() or "buyer"

print("---------------------------\n")

# Define the World (3 Variables)
space = OutcomeSpace(issues=[
    Issue(name="price", type="continuous", min_value=50, max_value=max(budget, ask)),
    Issue(name="service", type="discrete", values=["standard", "premium", "enterprise"]),
    Issue(name="duration", type="discrete", values=["1_year", "3_years"])
])

# --- 2. THE BUYER AGENT ---
class ConfigurableBuyer(BaseAgent):
    # DEFINE FIELDS HERE (Pydantic Style)
    use_meso: bool = True 
    
    def on_negotiation_start(self, state: AgentState):
        self.utility = LinearAdditiveUtility(
            weights={"price": w_price, "service": w_service, "duration": w_duration},
            outcome_space=space
        )
        
        # 1. Price Curve (Continuous)
        self.utility.add_curve("price", weight=w_price, invert=True) 
        
        # 2. Service Mapping (Discrete) <--- THIS WAS MISSING
        self.utility.add_discrete("service", weight=w_service, mapping={
            "standard": 0.0, 
            "premium": 0.7, 
            "enterprise": 1.0
        })
        
        # 3. Duration Mapping (Discrete) <--- THIS WAS MISSING
        self.utility.add_discrete("duration", weight=w_duration, mapping={
            "1_year": 0.0, 
            "3_years": 1.0
        })

    async def propose(self, state: AgentState) -> AgentResult:
        # Target drops slowly
        target = max(0.6, 0.85 - (state.step * 0.05))
        
        if self.use_meso:
            print(f"\n[Buyer] Strategy: MESO. Generating 3 packages (Target U={target:.2f})...")
            
            # Increased tolerance slightly to 0.08
            offers = generate_meso(self.utility, space, target, tolerance=0.08, max_offers=3)
            
            if not offers:
                print("   [Buyer] Could not find offers! Sending Fallback.")
                # Fallback: Best possible deal for Buyer
                return AgentResult(response="offer", proposal={"price": 50, "service": "enterprise", "duration": "3_years"})
            
            print(f"   [Buyer Generated] {len(offers)} Options:")
            for i, o in enumerate(offers):
                s = self.utility.calculate(o)
                print(f"     Option {i+1}: ${o['price']:.0f} | {o['service']} | {o['duration']} (Score: {s:.2f})")

            return AgentResult(response="offer", proposal=offers)
        else:
            print(f"\n[Buyer] Strategy: Simple. Generating best single offer (Target U={target:.2f})...")
            offers = generate_meso(self.utility, space, target, tolerance=0.08, max_offers=1)
            if not offers:
                 return AgentResult(response="offer", proposal={"price": 50, "service": "enterprise", "duration": "3_years"})
            return AgentResult(response="offer", proposal=offers[0])

    async def respond(self, state: AgentState) -> AgentResult:
        offer = state.current_offer
        if isinstance(offer, list): offer = offer[0]

        # Use the utility engine directly now!
        score = self.utility.calculate(offer)

        print(f"[Buyer] Evaluated Offer: {offer} -> Score: {score:.2f}")
        
        if score > 0.6: return AgentResult(response="accept")
        return AgentResult(response="reject")


# --- 3. THE SELLER AGENT ---
class SmartSeller(BaseAgent):
    def on_negotiation_start(self, state: AgentState):
        # Seller Preferences: Wants High Price, Low Service, Short Duration
        self.utility = LinearAdditiveUtility(
            weights={"price": 0.7, "service": 0.2, "duration": 0.1}, 
            outcome_space=space
        )
        self.utility.add_curve("price", weight=0.7, invert=False) # Higher is better

    async def propose(self, state: AgentState) -> AgentResult:
        # Stubborn Seller: Offers high price, standard service
        return AgentResult(response="offer", proposal={"price": ask, "service": "standard", "duration": "1_year"})

    async def respond(self, state: AgentState) -> AgentResult:
        incoming = state.current_offer
        
        # Helper to score a single item
        def rate(o):
            # Seller Math: Needs High Price
            p_score = (o['price'] - 50) / (max(budget, ask) - 50)
            # Service costs money, so Standard is best (1.0)
            s_map = {"standard": 1.0, "premium": 0.5, "enterprise": 0.0}
            return (p_score * 0.7) + (s_map.get(o['service'], 0) * 0.2)

        # 1. MESO Handling
        if isinstance(incoming, list):
            print(f"[Seller] Received {len(incoming)} options. Selecting best fit...")
            best_offer = max(incoming, key=rate)
            best_score = rate(best_offer)
            print(f"   [Seller] Best option found: {best_offer} (Score: {best_score:.2f})")
            
            if best_score > 0.6: return AgentResult(response="accept", proposal=best_offer)
            return AgentResult(response="reject")

        # 2. Single Offer Handling
        else:
            score = rate(incoming)
            print(f"[Seller] Received single offer. Score: {score:.2f}")
            if score > 0.6: return AgentResult(response="accept")
            return AgentResult(response="reject")

# --- 4. EXECUTION ---
async def main():
    config = NegotiationConfig(max_steps=6, time_limit=5.0, outcome_space=space)
    
    # Instantiate based on user choice using Pydantic arguments
    use_meso_flag = True if mode == "meso" else False
    
    # PASS 'name' EXPLICITLY HERE
    buyer = ConfigurableBuyer(name="Buyer", use_meso=use_meso_flag)
    seller = SmartSeller(name="Seller")
    
    # CONTROL THE ORDER HERE
    if initiator == "seller":
        print(f">>> STARTING (Seller Initiates)...")
        agents_list = [seller, buyer]
    else:
        print(f">>> STARTING (Buyer Initiates)...")
        agents_list = [buyer, seller]
        
    runner = Runner(config=config, agents=agents_list)
    result = await runner.run()
    
    if result.status == "success":
        print(f"\n>>> DEAL STRUCK! Final Agreement: {result.current_offer}")
    else:
        print(f"\n>>> FAILED: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())