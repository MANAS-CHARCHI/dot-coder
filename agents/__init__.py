# Task: AGENTS-INIT
# File: agents/__init__.py
# Description: Agent registry and dispatcher
# Author: System

from .sales import SalesAgent
from .manager import ManagerAgent
from .architect import ArchitectAgent
from .db_engineer import DBEngineerAgent
from .backend_engineer import BackendEngineerAgent
from .frontend_engineer import FrontendEngineerAgent
from .coder import CoderAgent
from .reviewer import ReviewerAgent
from .tester import TesterAgent
from .delivery import DeliveryAgent
from .setup_agent import SetupAgent


AGENT_MAP = {
    "sales": SalesAgent,
    "manager": ManagerAgent,
    "architect": ArchitectAgent,
    "setup": SetupAgent,
    "db_engineer": DBEngineerAgent,
    "backend_engineer": BackendEngineerAgent,
    "frontend_engineer": FrontendEngineerAgent,
    "coder_db": CoderAgent,
    "coder_backend": CoderAgent,
    "coder_frontend": CoderAgent,
    "reviewer_backend": ReviewerAgent,
    "reviewer_frontend": ReviewerAgent,
    "tester_backend": TesterAgent,
    "tester_frontend": TesterAgent,
    "final_tester": TesterAgent,
    "delivery": DeliveryAgent
}


def run_agent(agent_name: str, memory: dict, retry_count: int = 0) -> bool:
    """
    Run a specific agent by name.
    Returns True if successful, False otherwise.
    """
    agent_class = AGENT_MAP.get(agent_name)
    
    if not agent_class:
        print(f"Unknown agent: {agent_name}")
        return False
    
    # Instantiate and run
    agent = agent_class(agent_name, memory, retry_count)
    return agent.run()
