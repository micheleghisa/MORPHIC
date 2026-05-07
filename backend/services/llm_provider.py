"""
GLOWUP AI — LLM Provider
Provider agnostico: DeepSeek primario, Mistral fallback EU, OpenAI fallback.
GDPR-compliant: invia SOLO dati numerici anonimizzati, mai foto o nomi.
"""
import httpx
import json
import time
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from config import settings

logger = structlog.get_logger()


class LLMProvider:
    """Provider LLM agnostico con fallback automatico."""

    def __init__(self):
        self.provider = settings.llm_provider
        self._setup_clients()

    def _setup_clients(self):
        """Configura i client HTTP per ogni provider."""
        self.clients = {}

        if settings.deepseek_api_key:
            self.clients["deepseek"] = {
                "url": f"{settings.deepseek_base_url}/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                "model": settings.deepseek_model,
            }

        if settings.mistral_api_key:
            self.clients["mistral"] = {
                "url": "https://api.mistral.ai/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {settings.mistral_api_key}",
                    "Content-Type": "application/json",
                },
                "model": settings.mistral_model,
            }

        if settings.openai_api_key:
            self.clients["openai"] = {
                "url": "https://api.openai.com/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                "model": settings.openai_model,
            }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def _call_provider(
        self,
        provider_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> tuple[str, str]:
        """Chiama un provider specifico. Ritorna (contenuto, nome_provider)."""
        if provider_name not in self.clients:
            raise ValueError(f"Provider {provider_name} non configurato")

        client = self.clients[provider_name]
        payload = {
            "model": client["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=120.0) as http:
            response = await http.post(
                client["url"],
                headers=client["headers"],
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content, provider_name

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000,
        preferred_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera testo con fallback automatico.
        Ordine: preferred_provider > settings.llm_provider > mistral > openai.
        Ritorna {"content": ..., "provider": ..., "latency_ms": ...}
        """
        providers_order = []

        if preferred_provider and preferred_provider in self.clients:
            providers_order.append(preferred_provider)

        # Provider principale da config
        if settings.llm_provider in self.clients:
            if settings.llm_provider not in providers_order:
                providers_order.append(settings.llm_provider)

        # Fallback: Mistral (EU), poi OpenAI
        for fb in ["mistral", "openai"]:
            if fb in self.clients and fb not in providers_order:
                providers_order.append(fb)

        if not providers_order:
            raise RuntimeError("Nessun provider LLM configurato. Aggiungi almeno una API key.")

        last_error = None
        for provider_name in providers_order:
            try:
                start = time.time()
                content, used_provider = await self._call_provider(
                    provider_name, system_prompt, user_prompt, temperature, max_tokens
                )
                latency = (time.time() - start) * 1000

                logger.info(
                    "llm_call_success",
                    provider=used_provider,
                    latency_ms=round(latency, 1),
                    prompt_length=len(user_prompt),
                    response_length=len(content),
                )

                return {
                    "content": content,
                    "provider": used_provider,
                    "latency_ms": round(latency, 1),
                }
            except Exception as e:
                logger.warning("llm_call_failed", provider=provider_name, error=str(e))
                last_error = e
                continue

        raise RuntimeError(f"Tutti i provider LLM hanno fallito. Ultimo errore: {last_error}")


# ─── ISTANZA GLOBALE ───

_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider
