from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


class MemoryRecord(BaseModel):
    agent_name: str
    input_summary: Dict[str, Any]
    output_summary: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    feedback: Optional[str] = None


class WorkflowMemory(BaseModel):
    user_question: str
    records: List[MemoryRecord] = []
    user_feedback: Optional[str] = None

    def add_record(self, record: MemoryRecord) -> None:
        """Ajoute un enregistrement à la mémoire"""
        self.records.append(record)

    def get_recent_records(self, n: int = 5) -> List[MemoryRecord]:
        """Retourne les n derniers enregistrements"""
        return self.records[-n:] if self.records else []

    def to_context_string(self) -> str:
        """Convertit la mémoire en chaîne pour le contexte LLM"""
        context = f"Question utilisateur: {self.user_question}\n\n"
        context += "Historique des actions:\n"

        for record in self.records:
            context += f"\n- Agent: {record.agent_name}\n"
            context += f"  Timestamp: {record.timestamp}\n"
            context += f"  Input: {record.input_summary}\n"
            context += f"  Output: {record.output_summary}\n"
            if record.feedback:
                context += f"  Feedback: {record.feedback}\n"

        if self.user_feedback:
            context += f"\nFeedback utilisateur global: {self.user_feedback}\n"

        return context
