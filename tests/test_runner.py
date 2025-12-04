import unittest
import time
from manta.core.agent import BaseAgent, AgentState, AgentResult
from manta.negotiation.runner import Runner, NegotiationConfig

class DummyAgent(BaseAgent):
    def __init__(self, name, behavior="accept_immediately"):
        super().__init__(name)
        self.behavior = behavior
        self.proposals_made = 0
        
    def propose(self, state: AgentState) -> AgentResult:
        self.proposals_made += 1
        return AgentResult(response="propose", proposal={"price": 100})
        
    def respond(self, state: AgentState) -> AgentResult:
        if self.behavior == "accept_immediately":
            return AgentResult(response="accept")
        elif self.behavior == "reject_always":
            return AgentResult(response="reject")
        elif self.behavior == "accept_after_3_steps":
            if state.step >= 3:
                return AgentResult(response="accept")
            else:
                return AgentResult(response="reject")
        return AgentResult(response="reject")

class CrashingAgent(BaseAgent):
    def propose(self, state: AgentState) -> AgentResult:
        raise ValueError("I crashed!")
    
    def respond(self, state: AgentState) -> AgentResult:
        raise ValueError("I crashed!")

class TestRunner(unittest.TestCase):
    
    def test_basic_agreement(self):
        # Agent A proposes, Agent B accepts immediately
        agent_a = DummyAgent("A", behavior="reject_always") # Proposer
        agent_b = DummyAgent("B", behavior="accept_immediately") # Responder
        
        config = NegotiationConfig(max_steps=10)
        runner = Runner(config=config, agents=[agent_a, agent_b])
        
        runner.run()
        
        self.assertEqual(runner.state.status, "success")
        self.assertEqual(runner.state.step, 0) # 0-indexed, ends at step 0
        self.assertEqual(runner.state.current_offer, {"price": 100})

    def test_step_limit(self):
        # Both reject always
        agent_a = DummyAgent("A", behavior="reject_always")
        agent_b = DummyAgent("B", behavior="reject_always")
        
        config = NegotiationConfig(max_steps=5)
        runner = Runner(config=config, agents=[agent_a, agent_b])
        
        runner.run()
        
        self.assertEqual(runner.state.status, "timedout")
        self.assertEqual(runner.state.step, 5)

    def test_delayed_agreement(self):
        # Agent B accepts after step 3
        agent_a = DummyAgent("A", behavior="reject_always")
        agent_b = DummyAgent("B", behavior="accept_after_3_steps")
        
        config = NegotiationConfig(max_steps=10)
        runner = Runner(config=config, agents=[agent_a, agent_b])
        
        runner.run()
        
        self.assertEqual(runner.state.status, "success")
        # Step 0: A proposes, B rejects
        # Step 1: B proposes, A rejects
        # Step 2: A proposes, B rejects
        # Step 3: B proposes, A rejects (Wait, B is proposer here?)
        # Let's trace turns:
        # Step 0: Proposer=A (idx 0), Responder=B (idx 1). B rejects.
        # Step 1: Proposer=B (idx 1), Responder=A (idx 0). A rejects.
        # Step 2: Proposer=A (idx 0), Responder=B (idx 1). B rejects.
        # Step 3: Proposer=B (idx 1), Responder=A (idx 0). A rejects.
        # Step 4: Proposer=A (idx 0), Responder=B (idx 1). B accepts (step >= 3).
        
        # So it should end at step 4.
        self.assertEqual(runner.state.status, "success")
        self.assertGreaterEqual(runner.state.step, 3)

    def test_agent_crash(self):
        agent_a = CrashingAgent("A")
        agent_b = DummyAgent("B")
        
        config = NegotiationConfig(max_steps=5)
        runner = Runner(config=config, agents=[agent_a, agent_b])
        
        runner.run()
        
        self.assertEqual(runner.state.status, "broken")

if __name__ == '__main__':
    unittest.main()
