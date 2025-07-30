from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from ..models.memory import MemoryRecord


class BaseAgent(ABC):
    def __init__(
        self,
        name: Optional[str] = None,
        max_retries: int = 3,
        satisfaction_threshold: float = 0.7,
    ):
        self.name = name or self.__class__.__name__
        self.max_retries = max_retries
        self.satisfaction_threshold = satisfaction_threshold
        self.logger = logging.getLogger(self.name)

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Méthode principale de traitement"""
        pass

    @abstractmethod
    def evaluate_satisfaction(
        self,
        result: Any,
        *args,
        **kwargs,
    ) -> float:
        """Évalue la satisfaction du résultat"""
        pass

    def create_memory_record(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> MemoryRecord:
        """Crée un enregistrement mémoire"""
        return MemoryRecord(
            agent_name=self.name,
            input_summary=self._summarize_input(input_data),
            output_summary=self._summarize_output(output_data),
        )

    def _summarize_input(
        self,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Résume les données d'entrée pour la mémoire"""
        return {
            k: str(v)[:100] if isinstance(v, str) else v
            for k, v in input_data.items()
            if k not in ["memory", "context"]
        }

    def _summarize_output(
        self,
        output_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Résume les données de sortie pour la mémoire"""
        return {
            k: str(v)[:100] if isinstance(v, str) else v
            for k, v in output_data.items()
            if k not in ["memory", "debug_info"]
        }
