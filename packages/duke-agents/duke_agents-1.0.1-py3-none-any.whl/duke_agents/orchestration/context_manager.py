from typing import Any, Dict
from ..models.memory import WorkflowMemory
import json


class ContextManager:
    """Gestionnaire central du contexte et de la mémoire"""

    def __init__(self, user_question: str):
        self.workflow_memory = WorkflowMemory(user_question=user_question)
        self.global_context: Dict[str, Any] = {}
        self.agent_contexts: Dict[str, Dict[str, Any]] = {}

    def get_memory(self) -> WorkflowMemory:
        """Retourne la mémoire du workflow"""
        return self.workflow_memory

    def update_global_context(self, updates: Dict[str, Any]) -> None:
        """Met à jour le contexte global"""
        self.global_context.update(updates)

    def get_agent_context(self, agent_name: str) -> Dict[str, Any]:
        """Retourne le contexte spécifique d'un agent"""
        if agent_name not in self.agent_contexts:
            self.agent_contexts[agent_name] = {}
        return {
            **self.global_context,
            **self.agent_contexts[agent_name],
        }

    def update_agent_context(
        self,
        agent_name: str,
        updates: Dict[str, Any],
    ) -> None:
        """Met à jour le contexte spécifique d'un agent"""
        if agent_name not in self.agent_contexts:
            self.agent_contexts[agent_name] = {}
        self.agent_contexts[agent_name].update(updates)

    def add_user_feedback(self, feedback: str) -> None:
        """Ajoute le feedback utilisateur global"""
        self.workflow_memory.user_feedback = feedback

    def add_agent_feedback(self, agent_name: str, feedback: str) -> None:
        """Ajoute un feedback pour un agent spécifique"""
        for record in self.workflow_memory.records:
            if record.agent_name == agent_name and record.feedback is None:
                record.feedback = feedback
                break

    def save_state(self, filepath: str) -> None:
        """Sauvegarde l'état complet"""
        state: Dict[str, Any] = {
            "workflow_memory": self.workflow_memory.model_dump(),
            "global_context": self.global_context,
            "agent_contexts": self.agent_contexts,
        }
        with open(filepath, "w") as f:
            json.dump(
                state,
                f,
                indent=2,
                default=str,
            )

    @classmethod
    def load_state(cls, filepath: str) -> "ContextManager":
        """Charge l'état depuis un fichier"""
        with open(filepath, "r") as f:
            state = json.load(f)

        manager = cls(state["workflow_memory"]["user_question"])
        manager.workflow_memory = WorkflowMemory(**state["workflow_memory"])
        manager.global_context = state["global_context"]
        manager.agent_contexts = state["agent_contexts"]

        return manager
