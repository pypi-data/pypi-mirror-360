from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from .memory import WorkflowMemory


class CodeActInput(BaseModel):
    prompt: str
    data_context: Dict[str, Any]
    memory: WorkflowMemory


class CodeActOutput(BaseModel):
    success: bool
    generated_code: str
    execution_result: Any
    error: Optional[str] = None
    satisfaction_score: float = Field(ge=0.0, le=1.0)
    debug_info: Dict[str, Any] = Field(default_factory=dict)
    memory: WorkflowMemory
    
    @property
    def result(self) -> Any:
        """Propriété pour uniformiser l'interface avec AtomicOutput."""
        return self.execution_result
