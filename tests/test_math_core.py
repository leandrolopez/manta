import unittest
from manta.core.preferences import LinearAdditiveUtility, DiscreteValueFunction
from manta.core.pareto import find_pareto_frontier
from manta.core.meso import generate_meso

class TestMathCore(unittest.TestCase):

    def test_linear_additive_utility(self):
        # Setup
        weights = {"price": 0.6, "quantity": 0.4}
        
        # Price: 100 -> 1.0, 200 -> 0.0
        price_vf = DiscreteValueFunction({100: 1.0, 200: 0.0})
        
        # Quantity: 10 -> 0.0, 20 -> 1.0
        qty_vf = DiscreteValueFunction({10: 0.0, 20: 1.0})
        
        value_functions = {"price": price_vf, "quantity": qty_vf}
        
        utility_func = LinearAdditiveUtility(weights, value_functions, bias=0.1)
        
        # Test Case 1: Best outcome
        outcome1 = {"price": 100, "quantity": 20}
        # U = 0.1 + 0.6*1.0 + 0.4*1.0 = 1.1
        self.assertAlmostEqual(utility_func(outcome1), 1.1)
        
        # Test Case 2: Worst outcome
        outcome2 = {"price": 200, "quantity": 10}
        # U = 0.1 + 0.6*0.0 + 0.4*0.0 = 0.1
        self.assertAlmostEqual(utility_func(outcome2), 0.1)
        
        # Test Case 3: Mixed
        outcome3 = {"price": 100, "quantity": 10}
        # U = 0.1 + 0.6*1.0 + 0.4*0.0 = 0.7
        self.assertAlmostEqual(utility_func(outcome3), 0.7)

    def test_pareto_frontier(self):
        # Outcomes (just labels)
        outcomes = ["A", "B", "C", "D", "E"]
        
        # Utilities (Agent 1, Agent 2)
        # A: (1.0, 0.0)
        # B: (0.8, 0.8) - Likely Pareto
        # C: (0.5, 0.5) - Dominated by B
        # D: (0.0, 1.0)
        # E: (0.9, 0.1) - Dominated by A? No, A is (1.0, 0.0). E is worse for Ag1, better for Ag2.
        # Wait, A=(1,0), E=(0.9, 0.1). 
        # A vs E: A has 1.0 > 0.9, 0.0 < 0.1. Not dominated.
        
        # Let's make it clearer.
        # A: (10, 10) - Pareto
        # B: (5, 5) - Dominated by A
        # C: (12, 8) - Pareto
        # D: (8, 12) - Pareto
        # E: (9, 9) - Dominated by A (10,10)
        
        utilities = [
            (10.0, 10.0), # 0: A
            (5.0, 5.0),   # 1: B
            (12.0, 8.0),  # 2: C
            (8.0, 12.0),  # 3: D
            (9.0, 9.0)    # 4: E
        ]
        
        # Expected Frontier: A, C, D (indices 0, 2, 3)
        # B is dominated by A (and E)
        # E is dominated by A
        
        frontier_indices = find_pareto_frontier(outcomes, utilities)
        self.assertEqual(frontier_indices, [0, 2, 3])

    def test_meso_generation(self):
        # Outcome space: integers 0 to 10
        outcome_space = list(range(11))
        
        # Utility function: U(x) = x / 10.0
        def util_func(x):
            return x / 10.0
            
        # Target: 0.5, Tolerance: 0.1
        # Acceptable range: 0.4 to 0.6
        # Outcomes: 4 (0.4), 5 (0.5), 6 (0.6)
        
        meso = generate_meso(outcome_space, util_func, target_utility=0.5, tolerance=0.10001, size=2)
        
        # Should return 2 outcomes from [4, 5, 6]
        self.assertEqual(len(meso), 2)
        for item in meso:
            self.assertIn(item, [4, 5, 6])
            
        # Test with size > candidates
        meso_all = generate_meso(outcome_space, util_func, target_utility=0.5, tolerance=0.10001, size=5)
        self.assertEqual(len(meso_all), 3)
        self.assertEqual(set(meso_all), {4, 5, 6})

if __name__ == '__main__':
    unittest.main()
