from typing import Any

from config.settings import settings


class ModelRouter:
    def __init__(self) -> None:
        self.providers = {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
        }

    def select_model(self, task: str) -> str:
        return "openai" if self.providers["openai"] else "anthropic"


class PromptManager:
    def build_prompt(self, task: str, context: dict[str, Any] | None = None) -> str:
        return f"Task: {task}\nContext: {context or {}}"


class RetryLogic:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def run(self, fn, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return await fn(*args, **kwargs)
            except Exception:
                if attempt == self.max_retries - 1:
                    raise


class StructuredOutputValidator:
    def validate(self, output: Any) -> bool:
        return output is not None


class LLMWrapper:
    def __init__(self) -> None:
        self.router = ModelRouter()
        self.prompt_manager = PromptManager()
        self.retry = RetryLogic()
        self.validator = StructuredOutputValidator()

    async def generate(self, task: str, context: dict[str, Any] | None = None) -> Any:
        prompt = self.prompt_manager.build_prompt(task, context)
        model = self.router.select_model(task)
        return {"model": model, "prompt": prompt}
