import ast
from typing import Any, Dict, Tuple


def validate_code_safety(code: str) -> Tuple[bool, str]:
    """Valide que le code est sûr à exécuter"""
    forbidden_imports = [
        "os",
        "subprocess",
        "sys",
        "__import__",
    ]
    forbidden_builtins = [
        "eval",
        "exec",
        "compile",
        "__import__",
    ]

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_imports:
                        return False, f"Import forbidden: {alias.name}"
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in forbidden_builtins:
                    return False, f"Forbidden function: {node.func.id}"
        return True, "Code is safe"
    except SyntaxError as e:
        return False, f"Syntax error: {e}"


def extract_variables(
    code: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Extrait les variables définies dans le code"""
    exec_globals: Dict[str, Any] = context.copy() if context else {}
    try:
        exec(code, exec_globals)
    except Exception:
        return {}

    result_vars: Dict[str, Any] = {}
    for key, value in exec_globals.items():
        if key not in (context or {}) and not key.startswith("__"):
            result_vars[key] = value
    return result_vars
