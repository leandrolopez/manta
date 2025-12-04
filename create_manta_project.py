import os

# ---------------------------
# CONFIGURATION
# ---------------------------
project_name = "manta"
author_name = "Antonio L. Lopez"
email = "lopezcamejo@gmail.com"

# ---------------------------
# NOTICE CONTENT
# ---------------------------
notice_content = (
    "MANTA - Multi-Agent Negotiation & Task Automation\n"
    "Copyright 2025\n\n"
    f"Developed by {author_name}"
)

# ---------------------------
# FOLDER STRUCTURE
# ---------------------------
folders = [
    f"{project_name}/assets",
    f"{project_name}/{project_name}/core",
    f"{project_name}/{project_name}/negotiation/strategies",
    f"{project_name}/{project_name}/tasks/planners",
    f"{project_name}/{project_name}/utils",
    f"{project_name}/{project_name}/api",
    f"{project_name}/tests",
    f"{project_name}/examples",
    f"{project_name}/docs",
]

# ---------------------------
# FILES TO CREATE
# ---------------------------
files = {
    "NOTICE": notice_content,
    "pyproject.toml": f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "MANTA — Multi-Agent Negotiation & Task Automation"
readme = "README.md"
authors = [{{ name="{author_name}", email="{email}" }}]
requires-python = ">=3.9"
license = {{ text = "Apache-2.0" }}

[project.urls]
Homepage = "https://github.com/YOURNAME/{project_name}"
Issues = "https://github.com/YOURNAME/{project_name}/issues"
Documentation = "https://YOUR-DOCS-SITE"
""",
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*.egg-info/
*.egg
dist/
build/

# IDEs
.vscode/
.idea/
*.iml

# Environments
.env
.venv/
""",
    # Core modules
    f"{project_name}/{project_name}/__init__.py": "",
    f"{project_name}/{project_name}/core/__init__.py": "",
    f"{project_name}/{project_name}/core/agent.py": """class Agent:
    def __init__(self, name: str):
        self.name = name

    def act(self, observation):
        pass
""",
    f"{project_name}/{project_name}/core/environment.py": "",
    f"{project_name}/{project_name}/core/negotiation.py": """class NegotiationProtocol:
    def __init__(self, agents):
        self.agents = agents

    def run(self):
        return "Negotiation result placeholder"
""",
    f"{project_name}/{project_name}/core/protocol.py": "",
    f"{project_name}/{project_name}/core/task.py": "",
    # Negotiation
    f"{project_name}/{project_name}/negotiation/__init__.py": "",
    f"{project_name}/{project_name}/negotiation/models.py": "",
    # Tasks
    f"{project_name}/{project_name}/tasks/__init__.py": "",
    f"{project_name}/{project_name}/tasks/workflow.py": "",
    # Utils
    f"{project_name}/{project_name}/utils/__init__.py": "",
    f"{project_name}/{project_name}/utils/logging.py": "",
    f"{project_name}/{project_name}/utils/data.py": "",
    # API
    f"{project_name}/{project_name}/api/__init__.py": "",
    f"{project_name}/{project_name}/api/high_level.py": "",
    f"{project_name}/{project_name}/api/server.py": "",
    # Tests
    f"{project_name}/tests/test_agents.py": """from manta.core.agent import Agent

def test_agent_creation():
    agent = Agent("TestAgent")
    assert agent.name == "TestAgent"
""",
    f"{project_name}/tests/test_negotiation.py": "",
    f"{project_name}/tests/test_tasks.py": "",
    # Examples
    f"{project_name}/examples/basic_negotiation.py": "",
    f"{project_name}/examples/multi_agent_demo.py": "",
    # Docs
    f"{project_name}/docs/index.md": "",
    # Assets
    f"{project_name}/assets/manta-logo.png": "",
}

# ---------------------------
# CREATE FOLDERS
# ---------------------------
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ---------------------------
# CREATE FILES
# ---------------------------
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"✅ MANTA starter project created in ./{project_name}/")
