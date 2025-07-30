"""AI integration module for TicketPlease."""

import litellm

from .prompts import (
    get_github_format_instructions,
    get_jira_format_instructions,
    get_refinement_prompt,
    get_task_generation_prompt,
)


class AIService:
    """Service for interacting with AI models."""

    def __init__(self, provider: str, api_key: str, model: str) -> None:
        """Initialize the AI service."""
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self._setup_litellm()

    def _setup_litellm(self) -> None:
        """Setup litellm configuration."""
        litellm.api_key = self.api_key
        litellm.set_verbose = False

    def _get_completion(self, prompt: str, error_message: str) -> str:
        """Get completion from LLM with standardized parameters."""
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"{error_message}: {e}") from e

    def generate_task_description(
        self,
        task_description: str,
        acceptance_criteria: list[str],
        definition_of_done: list[str],
        platform: str,
        language: str,
    ) -> str:
        """Generate a task description using AI."""
        prompt = self._build_prompt(
            task_description,
            acceptance_criteria,
            definition_of_done,
            platform,
            language,
        )
        return self._get_completion(prompt, "Error generating task description")

    def refine_task_description(self, current_description: str, refinement_request: str) -> str:
        """Refine an existing task description."""
        prompt = get_refinement_prompt(current_description, refinement_request)
        return self._get_completion(prompt, "Error refining task description")

    def _build_prompt(
        self,
        task_description: str,
        acceptance_criteria: list[str],
        definition_of_done: list[str],
        platform: str,
        language: str,
    ) -> str:
        """Build the prompt for task description generation."""
        ac_text = "\n".join(f"- {criterion}" for criterion in acceptance_criteria)
        dod_text = "\n".join(f"- {item}" for item in definition_of_done)

        if platform.lower() == "github":
            format_instructions = get_github_format_instructions()
        else:  # Jira
            format_instructions = get_jira_format_instructions()

        return get_task_generation_prompt(
            task_description, ac_text, dod_text, format_instructions, language
        )
