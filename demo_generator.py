from manta.core.outcomes import OutcomeSpace, Issue
from manta.core.preferences import LinearAdditiveUtility
from manta.core.meso import generate_meso 

def main():
    print("\n=== MANTA MESO GENERATOR (Production Mode) ===")
    
    # 1. DEFINE THE WORLD
    # In a real app, this comes from a database config
    space = OutcomeSpace(issues=[
        Issue(name="price", type="continuous", min_value=50, max_value=200),
        Issue(name="service", type="discrete", values=["standard", "premium", "enterprise"]),
        Issue(name="duration", type="discrete", values=["1_year", "3_years"]),
        Issue(name="payment", type="discrete", values=["net30", "net60", "upfront"])
    ])
    
    print(f"\n[Scope] Negotiating 4 Variables: Price ($50-200), Service, Duration, Payment")

    # 2. DEFINE PREFERENCES (The "Brain")
    # This maps what you care about to a score of 0.0-1.0
    weights = {
        "price": 0.5,      # I care 50% about price
        "service": 0.3,    # I care 30% about service quality
        "duration": 0.1,   # I care 10% about term length
        "payment": 0.1     # I care 10% about payment terms
    }
    
    utility = LinearAdditiveUtility(weights=weights, outcome_space=space)
    
    # We must explicitly define the min/max of the curve using the OutcomeSpace bounds (50-200)
    utility.add_curve(
        "price", 
        weight=0.5, 
        min_val=50.0, 
        max_val=200.0, # Using the max defined in the OutcomeSpace above
        invert=True
    )
    
  

    # 3. INTERACTIVE GENERATION LOOP
    while True:
        print("\n------------------------------------------------")
        target_input = input("Enter Target Utility (0.1 - 1.0) or 'q' to quit: ")
        if target_input.lower() == 'q': break
        
        try:
            target = float(target_input)
        except ValueError:
            print("Invalid number.")
            continue
            
        print(f"\n[Manta] Searching for 3 distinct offers worth exactly {target:.2f} (±5%)...")
        
        # --- THE CORE LIBRARY FUNCTION ---
        # This is the "Product" you wanted. Pure generation.
        offers = generate_meso(
            utility_function=utility,
            outcome_space=space,
            target_utility=target,
            tolerance=0.05,
            max_offers=3
        )
        
        if not offers:
            print("❌ No offers found. Your target might be mathematically impossible.")
            print("   (e.g., You asked for 1.0 utility, but that requires Perfect Price + Perfect Service)")
        else:
            print(f"✅ Generated {len(offers)} MESO Options:")
            for i, offer in enumerate(offers):
                # Recalculate score to show accuracy
                # Note: We do a manual calc for display to show the "Why"
                real_score = utility.calculate(offer)
                # Manual bonus display logic (since linear utility is generic)
                #bonus = 0.0
                #if offer['service'] == 'premium': bonus += 0.15
                #if offer['service'] == 'enterprise': bonus += 0.3
                #if offer['payment'] == 'upfront': bonus += 0.1
                
                final_score = real_score
                
                print(f"   Option {i+1}: Price ${offer['price']:.0f} | {offer['service']} | {offer['duration']} | {offer['payment']}")
                print(f"             (Base Score: {real_score:.2f} + Bonuses -> Final: {final_score:.2f})")

if __name__ == "__main__":
    main()