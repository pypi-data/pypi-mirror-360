from typing import Any, Dict, List, Union
from ..models.atomic_models import AtomicOutput
from ..models.codeact_models import CodeActOutput
import json


def create_workflow_summary(
    results: List[Union[AtomicOutput, CodeActOutput]],
) -> Dict[str, Any]:
    """Crée un résumé du workflow"""
    summary = {
        "total_steps": len(results),
        "successful_steps": sum(1 for r in results if r.success),
        "failed_steps": sum(1 for r in results if not r.success),
        "average_satisfaction": 0.0,
        "steps": [],
    }

    total = 0.0
    for i, r in enumerate(results):
        step = {
            "step": i + 1,
            "success": r.success,
            "satisfaction_score": r.satisfaction_score,
            "error": r.error,
        }
        if isinstance(r, CodeActOutput):
            step["type"] = "CodeAct"
            step["code_length"] = len(r.generated_code)
        else:
            step["type"] = "Atomic"

        summary["steps"].append(step)  # type: ignore
        total += r.satisfaction_score

    if results:
        summary["average_satisfaction"] = total / len(results)
    return summary


def save_workflow_results(
    results: List[Union[AtomicOutput, CodeActOutput]],
    filepath: str,
) -> None:
    """Sauvegarde les résultats du workflow"""
    serial = []
    for r in results:
        d = r.model_dump()
        if "execution_result" in d and d["execution_result"] is not None:
            d["execution_result"] = str(d["execution_result"])
        serial.append(d)

    with open(filepath, "w") as f:
        json.dump(serial, f, indent=2)


def create_workflow_from_yaml(
    yaml_content: str,
) -> List[Dict[str, Any]]:
    """Crée un workflow depuis un fichier YAML"""
    import yaml

    data = yaml.safe_load(yaml_content)
    steps = []
    for s in data.get("steps", []):
        steps.append(
            {
                "agent": s["agent"],
                "input_type": s.get("type", "atomic"),
                "input_data": s.get("input", {}),
                "continue_on_failure": s.get("continue_on_failure", False),
            }
        )
    return steps
