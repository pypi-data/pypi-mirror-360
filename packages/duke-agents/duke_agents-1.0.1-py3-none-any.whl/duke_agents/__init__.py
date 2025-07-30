"""
DUKE Agents - Advanced AI Agent Framework

Example usage:
    from duke_agents import AtomicAgent, CodeActAgent, Orchestrator
    from duke_agents.orchestration import ContextManager

    # Initialize context
    context = ContextManager("Analyze this data")

    # Create orchestrator
    orchestrator = Orchestrator(context)

    # Register agents
    orchestrator.register_agent(AtomicAgent("data_processor"))
    orchestrator.register_agent(CodeActAgent("code_generator"))
"""

from .__version__ import __version__, __author__, __email__

# Import core components
from .models import (
    WorkflowMemory,
    MemoryRecord,
    AtomicInput,
    AtomicOutput,
    CodeActInput,
    CodeActOutput,
)

from .agents import BaseAgent, AtomicAgent, CodeActAgent

from .orchestration import ContextManager, Orchestrator

from .executors import CodeExecutor
from .llm import MistralClient

# Convenience imports
from .config import Config

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Models
    "WorkflowMemory",
    "MemoryRecord",
    "AtomicInput",
    "AtomicOutput",
    "CodeActInput",
    "CodeActOutput",
    # Agents
    "BaseAgent",
    "AtomicAgent",
    "CodeActAgent",
    # Orchestration
    "ContextManager",
    "Orchestrator",
    # Executors
    "CodeExecutor",
    # LLM
    "MistralClient",
    # Config
    "Config",
]

# Package metadata
__package_name__ = "duke-agents"
__description__ = "Advanced AI Agent Framework with IPO Architecture"
