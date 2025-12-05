import asyncio
import sys
from typing import List, Union, Literal
from manta.core.outcomes import OutcomeSpace, Issue
from manta.core.preferences import LinearAdditiveUtility
from manta.core.meso import generate_meso 

# --- 1. CORE SETUP ---
# Defining the world once globally for all tests
SPACE = OutcomeSpace(issues=[
    Issue(name="price", type="continuous", min_value=50.0, max_value=200.0),
    Issue(name="service", type="discrete", values=["standard", "premium", "enterprise"]),
    Issue(name="duration", type="discrete", values=["1_year", "3_years"]),
    Issue(name="payment", type="discrete", values=["net30", "net60", "upfront"]),
])

# Defining the Brain once globally
UTILITY = LinearAdditiveUtility(weights={"price": 0.6, "service": 0.3, "duration": 0.1}, outcome_space=SPACE)
UTILITY.add_curve("price", weight=0.6, min_val=50.0, max_val=200.0, invert=True)

TARGET = 0.80
TOLERANCE_GS = 0.15 # Wide tolerance for Grid Search (to catch guaranteed points)
TOLERANCE_MC = 0.08 # Medium tolerance for Monte Carlo (to keep results tight)

# --- 2. THE TEST FUNCTION ---

def run_generator_test(
    method: Literal['grid_search', 'monte_carlo'],
    target_score: float,
    tolerance: float
) -> List[dict]:
    """Runs the MESO generator with specified method and returns offers."""
    
    # We will use max_offers=5 for GS and max_offers=3 for MC
    max_o = 5 if method == 'grid_search' else 3
    
    print(f"\n[{method.upper()}] Searching (Target U: {target_score:.2f}, Tol: {tolerance})...")
    
    # The core logic: call generate_meso with the explicit method
    offers = generate_meso(
        utility_function=UTILITY,
        outcome_space=SPACE,
        target_utility=target_score,
        tolerance=tolerance,
        max_offers=max_o,
        method=method 
    )

    if not offers:
        print("    ❌ FAILED: Could not find offers.")
        return []

    print(f"    ✅ SUCCESS: Found {len(offers)} Offers:")
    for i, offer in enumerate(offers):
        final_score = UTILITY.calculate(offer)
        print(f"       Option {i+1}: ${offer['price']:.0f} | {offer['service']} | {offer['duration']} | {offer.get('payment', 'N/A')} (Score: {final_score:.4f})")

        
    
    return offers

# --- 3. THE INTERACTIVE CLI ---

def main():
    while True:
        print("\n=== MANTA GENERATOR TEST MENU ===")
        print("1: Grid Search (Deterministic/Reliable)")
        print("2: Monte Carlo (Random/Flexible)")
        print("3: Run Both & Compare")
        print("q: Quit")
        
        choice = input("Enter choice (1/2/3/q): ")
        
        if choice.lower() == 'q':
            sys.exit()
        
        # Determine methods to run
        methods_to_run = []
        if choice == '1':
            methods_to_run = ['grid_search']
        elif choice == '2':
            methods_to_run = ['monte_carlo']
        elif choice == '3':
            methods_to_run = ['grid_search', 'monte_carlo']
        else:
            print("Invalid choice. Try again.")
            continue
            
        # Run the tests based on selection
        for method in methods_to_run:
            if method == 'grid_search':
                run_generator_test(method, TARGET, TOLERANCE_GS)
            else:
                run_generator_test(method, TARGET, TOLERANCE_MC)

if __name__ == "__main__":
    main()