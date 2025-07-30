import subprocess
import tempfile
import os
import sys
import io
import json
import traceback
from typing import Any, Dict, Tuple, Optional

from ..config import Config


class CodeExecutor:
    def __init__(
        self,
        timeout: Optional[int] = None,
    ):
        self.timeout = timeout or Config.CODE_EXECUTION_TIMEOUT

    def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, str, bool]:
        """
        Exécute du code Python de manière sécurisée
        Returns: (result, output, success)
        """
        if Config.ENABLE_SANDBOXED_EXECUTION:
            return self._execute_sandboxed(
                code,
                context,
            )
        return self._execute_unsafe(
            code,
            context,
        )

    def _execute_sandboxed(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, str, bool]:
        """Exécution dans un sous-processus isolé"""
        # Préparer un fichier temporaire
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            setup_code = ""
            if context:
                # Sérialiser le contexte de manière sécurisée
                setup_code = (
                    "import json\n"
                    f"context = json.loads({json.dumps(json.dumps(context))})\n"
                    "globals().update(context)\n\n"
                )
            f.write(setup_code + code)
            f.flush()
            try:
                proc = subprocess.run(
                    [sys.executable, f.name],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                if proc.returncode == 0:
                    return proc.stdout, proc.stdout, True
                return None, proc.stderr, False

            except subprocess.TimeoutExpired:
                msg = f"Code execution timed out after {self.timeout} seconds"
                return None, msg, False
            except Exception as e:
                err = str(e)
                return None, err, False
            finally:
                try:
                    os.unlink(f.name)
                except OSError:
                    pass

    def _execute_unsafe(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, str, bool]:
        """Exécution directe (moins sûre mais plus flexible)"""
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        exec_globals = {"__builtins__": __builtins__}
        if context:
            exec_globals.update(context)
        try:
            exec(code, exec_globals)
            output = sys.stdout.getvalue()
            result = exec_globals.get("result", output)
            return result, output, True
        except Exception as e:
            trace = traceback.format_exc()
            err_msg = (
                f"{type(e).__name__}: {e}\n"
                f"{trace}"
            )
            return None, err_msg, False
        finally:
            sys.stdout = old_stdout
