from typing import Any, Optional
import traceback

from ..models.atomic_models import AtomicInput, AtomicOutput
from .base_agent import BaseAgent


class AtomicAgent(BaseAgent):
    def __init__(
        self,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(name=name, **kwargs)

    def run(
        self,
        input_data: AtomicInput,
    ) -> AtomicOutput:
        """Point d'entrée principal avec auto-correction"""
        attempts = 0
        last_error = None

        while attempts < self.max_retries:
            try:
                if last_error:
                    input_data.context["last_error"] = last_error
                    input_data.context["attempts"] = attempts

                result = self.process(input_data)
                score = self.evaluate_satisfaction(
                    result,
                    input_data,
                )

                record = self.create_memory_record(
                    input_data={
                        "task_id": input_data.task_id,
                        "parameters": input_data.parameters,
                    },
                    output_data={
                        "result": result,
                        "satisfaction_score": score,
                    },
                )
                input_data.memory.add_record(record)

                if score >= self.satisfaction_threshold:
                    return AtomicOutput(
                        success=True,
                        result=result,
                        satisfaction_score=score,
                        memory=input_data.memory,
                        debug_info={
                            "attempts": attempts + 1,
                        },
                    )

                last_error = (
                    "Satisfaction score too low: "
                    + str(score)
                )

            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                self.logger.error(
                    f"Attempt {attempts + 1} failed: "
                    f"{last_error}"
                )
                self.logger.debug(traceback.format_exc())

            attempts += 1

        return AtomicOutput(
            success=False,
            result=None,
            error=(
                "Failed after "
                + str(attempts)
                + " attempts. "
                + f"Last error: {last_error}"
            ),
            satisfaction_score=0.0,
            memory=input_data.memory,
            debug_info={
                "attempts": attempts,
                "last_error": last_error,
            },
        )

    def process(
        self,
        input_data: AtomicInput,
    ) -> Any:
        """Traitement principal - à surcharger dans les sous-classes"""
        self.logger.info(
            f"Processing task {input_data.task_id}"
        )
        return (
            f"Processed task {input_data.task_id} "
            f"with parameters {input_data.parameters}"
        )

    def evaluate_satisfaction(
        self,
        result: Any,
        input_data: AtomicInput,
    ) -> float:
        """Évaluation par défaut - à surcharger dans les sous-classes"""
        if result is None:
            return 0.0
        if (
            isinstance(result, str)
            and "error" in result.lower()
        ):
            return 0.3
        return 0.8
