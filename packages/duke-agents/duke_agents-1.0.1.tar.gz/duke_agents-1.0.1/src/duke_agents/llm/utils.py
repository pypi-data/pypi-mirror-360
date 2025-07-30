import re
from typing import Optional, Tuple


def extract_code_block(text: str) -> Optional[str]:
    """Extrait le code entre les balises <execute>"""
    pattern = r"<execute>(.*?)</execute>"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None


def parse_satisfaction_reasoning(text: str) -> Tuple[float, str]:
    """Parse le raisonnement de satisfaction du LLM"""
    score_pattern = r"satisfaction_score:\s*(\d+\.?\d*)"
    reason_pattern = r"reason:\s*(.+?)(?=\n|$)"

    score_match = re.search(score_pattern, text, re.IGNORECASE)
    reason_match = re.search(reason_pattern, text, re.IGNORECASE)

    score = float(score_match.group(1)) if score_match else 0.5
    reason = reason_match.group(1) if reason_match else "No reason provided"

    return min(max(score, 0.0), 1.0), reason
