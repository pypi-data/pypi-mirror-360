from typing import Dict, Any, List, Type, Optional
from .base_agent import BaseAgent
from .atomic_agent import AtomicAgent
from .codeact_agent import CodeActAgent

# Global registry for agents
_agent_registry: Dict[str, Type[BaseAgent]] = {}


def register_agent(agent_class: Type[BaseAgent], name: Optional[str] = None) -> None:
    """Enregistre un agent dans le registre global"""
    agent_name = name or agent_class.__name__
    _agent_registry[agent_name] = agent_class


def get_agent(name: str) -> Type[BaseAgent]:
    """Récupère un agent du registre"""
    if name not in _agent_registry:
        raise ValueError(f"Agent '{name}' not found in registry")

    return _agent_registry[name]


def list_agents() -> List[str]:
    """Liste tous les agents enregistrés"""
    return list(_agent_registry.keys())


def create_agent_from_config(config: Dict[str, Any]) -> BaseAgent:
    """Crée un agent à partir d'une configuration"""
    agent_type = config.get("type", "AtomicAgent")
    agent_name = config.get("name", agent_type)
    params = config.get("params", {})

    if agent_type == "AtomicAgent":
        return AtomicAgent(name=agent_name, **params)
    elif agent_type == "CodeActAgent":
        return CodeActAgent(name=agent_name, **params)
    else:
        # Essayer de charger depuis le registre
        agent_class = get_agent(agent_type)
        return agent_class(name=agent_name, **params)


# Enregistrer les agents de base
register_agent(AtomicAgent)
register_agent(CodeActAgent)