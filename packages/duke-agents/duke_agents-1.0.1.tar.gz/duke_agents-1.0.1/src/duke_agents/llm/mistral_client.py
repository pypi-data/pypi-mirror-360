from typing import Any, Dict, Optional, List

from mistralai import Mistral

from ..config import Config


class MistralClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        self.api_key = api_key or Config.MISTRAL_API_KEY
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY is required")
        self.client = Mistral(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Génère une réponse avec Mistral"""
        model = model or Config.MISTRAL_MODEL

        messages: List[Dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        if isinstance(content, str):
            return content
        else:
            # Handle case where content might be list or None
            return str(content) if content else ""

    def generate_code(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.3,
    ) -> str:
        """Génère du code avec Codestral"""
        system_prompt = (
            "You are an expert Python developer."
            " Generate clean, efficient, and well-documented code."
            " Always wrap your code in <execute>...</execute> tags."
        )
        if context:
            full_prompt = f"Context: {context}\n\n{prompt}"
        else:
            full_prompt = prompt

        return self.generate(
            prompt=full_prompt,
            model=Config.CODESTRAL_MODEL,
            temperature=temperature,
            system_prompt=system_prompt,
        )
