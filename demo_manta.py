import asyncio
from manta.core.outcomes import OutcomeSpace, Issue
from manta.negotiation.runner import Runner, NegotiationConfig
# Import the Universal Agent
from manta.agents.standard import StandardAgent

# 1. DEFINE THE WORLD (Once)
space = OutcomeSpace(issues=[
    Issue(name="price", type="continuous", min_value=50, max_value=150),
    Issue(name="service", type="discrete", values=["standard", "premium", "enterprise"]),
    Issue(name="duration", type="discrete", values=["1_year", "3_years"])
])

# 2. CONFIGURE AGENT A (The Buyer)
# Imagine this data came from a Database or API Request
buyer_config = {
    "name": "Acme Corp Bot",
    "role": "buyer",
    "outcome_space": space,
    "weights": {"price": 0.6, "service": 0.3, "duration": 0.1},
    "personality": "linear",
    "reservation_val": 0.5
}

# 3. CONFIGURE AGENT B (The Seller)
seller_config = {
    "name": "SaaS Vendor Bot",
    "role": "seller",
    "outcome_space": space,
    "weights": {"price": 0.7, "service": 0.2, "duration": 0.1},
    "personality": "conceder",
    "reservation_val": 0.5
}

# 4. RUN THE ENGINE
async def main():
    # Instantiate using arguments - NO NEW CLASS DEFINITIONS
    buyer = StandardAgent(**buyer_config)
    seller = StandardAgent(**seller_config)
    
    config = NegotiationConfig(max_steps=10, time_limit=5.0, outcome_space=space)
    runner = Runner(config=config, agents=[buyer, seller])
    
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())