from typing import Any, Dict, Optional, List

from ..models.codeact_models import CodeActInput, CodeActOutput
from .base_agent import BaseAgent
from ..llm.mistral_client import MistralClient
from ..llm.utils import extract_code_block, parse_satisfaction_reasoning
from ..executors.code_executor import CodeExecutor


class CodeActAgent(BaseAgent):
    def __init__(
        self,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(name=name, **kwargs)
        self.llm_client = MistralClient()
        self.code_executor = CodeExecutor()

    def run(
        self,
        input_data: CodeActInput,
    ) -> CodeActOutput:
        """Point d'entrée principal avec génération et exécution de code"""
        attempts = 0
        last_error: Optional[str] = None
        generated: List[str] = []

        while attempts < self.max_retries:
            try:
                prompt = self._prepare_prompt(
                    input_data.prompt,
                    input_data.data_context,
                    input_data.memory,
                    last_error,
                    attempts,
                )
                llm_resp = self.llm_client.generate_code(
                    prompt=prompt,
                    context=input_data.data_context,
                )
                code = extract_code_block(llm_resp)
                if not code:
                    raise ValueError("No code found in LLM response")
                generated.append(code)

                res, out, ok = self.code_executor.execute(
                    code,
                    input_data.data_context,
                )
                if not ok:
                    last_error = out
                    attempts += 1
                    continue

                score = self.evaluate_satisfaction(
                    res,
                    out,
                    input_data,
                )
                record = self.create_memory_record(
                    input_data={
                        "prompt": input_data.prompt[:200],
                        "ctx_keys": list(input_data.data_context),
                    },
                    output_data={
                        "code_len": len(code),
                        "success": ok,
                        "score": score,
                    },
                )
                input_data.memory.add_record(record)

                if score >= self.satisfaction_threshold:
                    return CodeActOutput(
                        success=True,
                        generated_code=code,
                        execution_result=res,
                        satisfaction_score=score,
                        memory=input_data.memory,
                        debug_info={
                            "attempts": attempts + 1,
                            "output": out,
                            "all_codes": generated,
                        },
                    )
                last_error = f"Low satisfaction: {score}"

            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                self.logger.error(
                    f"Attempt {attempts+1} failed: {last_error}"
                )
            attempts += 1

        return CodeActOutput(
            success=False,
            generated_code=generated[-1] if generated else "",
            execution_result=None,
            error=(
                "Failed after " + str(attempts)
                + " attempts. Last error: "
                + str(last_error)
            ),
            satisfaction_score=0.0,
            memory=input_data.memory,
            debug_info={
                "attempts": attempts,
                "last_error": last_error,
                "all_codes": generated,
            },
        )

    def _prepare_prompt(
        self,
        prompt: str,
        context: Dict[str, Any],
        memory: Any,
        last_error: Optional[str],
        attempts: int,
    ) -> str:
        """Prépare le prompt enrichi pour le LLM"""
        parts: List[str] = []
        parts.append(
            "Memory Context:\n" + memory.to_context_string()
        )
        parts.append(f"Current Task: {prompt}\n")
        if context:
            parts.append("Data Context:")
            for k, v in context.items():
                parts.append(f"- {k}: {str(v)[:100]}...")
            parts.append("")
        if last_error:
            parts.append(
                "Previous attempt failed:\n" + last_error
            )
            parts.append(
                f"This is attempt {attempts+1}. Fix the issue."
            )
        parts.append(
            "Generate Python code that:\n"
            "1. Solves the given task\n"
            "2. Uses the provided context\n"
            "3. Includes error handling\n"
            "4. Returns a result that can be eval\n"
            "5. Includes tests for correctness\n"
            "Wrap code in <execute> tags."
        )
        return "\n\n".join(parts)

    def evaluate_satisfaction(
        self,
        result: Any,
        output: str,
        input_data: CodeActInput,
    ) -> float:
        """Évalue la satisfaction basée sur le résultat et les tests"""
        prompt = (
            "Evaluate code execution result:\n"
            f"Task: {input_data.prompt}\n"
            f"Output: {output}\n"
            f"Result: {result}\n\n"
            "Rate score 0.0-1.0 on correctness, expected output, errors.\n"
            "Respond as 'satisfaction_score: X.X'"
        )
        resp = self.llm_client.generate(
            prompt=prompt,
            temperature=0.1,
        )
        score, _ = parse_satisfaction_reasoning(resp)
        self.logger.info(f"Eval satisfaction: {score}")
        return score

    def process(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Non utilisé: utilisez run() à la place"""
        raise NotImplementedError(
            "Use run() for CodeActAgent"
        )
