from manta.core.agent import Agent

def test_agent_creation():
    agent = Agent("TestAgent")
    assert agent.name == "TestAgent"
