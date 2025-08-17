from app.agents.sales_assistants.orchestrator_agent import orchestrator_agent

_orchestrator = None


def initialize_orchestrator():
    global _orchestrator
    _orchestrator = orchestrator_agent
    return _orchestrator


def get_orchestrator():
    if _orchestrator is None:
        raise Exception("Orchestrator not initialized")
    return _orchestrator
