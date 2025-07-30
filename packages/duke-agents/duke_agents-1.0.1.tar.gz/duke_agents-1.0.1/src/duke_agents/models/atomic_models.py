from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from .memory import WorkflowMemory


class AtomicInput(BaseModel):
    task_id: str
    parameters: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)
    memory: WorkflowMemory


class AtomicOutput(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    satisfaction_score: float = Field(ge=0.0, le=1.0)
    debug_info: Dict[str, Any] = Field(default_factory=dict)
    memory: WorkflowMemory
