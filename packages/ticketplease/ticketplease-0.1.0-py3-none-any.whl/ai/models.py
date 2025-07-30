"""AI model management and retrieval from LiteLLM."""

import litellm


class ModelProvider:
    """Manages AI model retrieval and organization by provider."""

    @staticmethod
    def get_supported_models() -> dict[str, list[str]]:
        """Return a dictionary of provider -> list of supported models using litellm provider-specific lists."""
        models_by_provider = {
            "openai": ModelProvider.get_openai_models(),
            "anthropic": ModelProvider.get_anthropic_models(),
            "gemini": ModelProvider.get_gemini_models(),
            "openrouter": ModelProvider.get_openrouter_models(),
        }

        # Add custom model option to each provider
        for provider in models_by_provider:
            models_by_provider[provider].append("🔧 Specify custom model")

        return models_by_provider

    @staticmethod
    def get_openai_models() -> list[str]:
        """Get OpenAI models from litellm."""
        # Use litellm's OpenAI-specific model list
        openai_models = litellm.open_ai_chat_completion_models

        # Filter out fine-tuned and special models
        filtered_models = [
            m
            for m in openai_models
            if not m.startswith("ft:") and not m.startswith("omni-") and "gpt" in m.lower()
        ]

        # Preferred order - exact matches first, then partial matches
        preferred_exact = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
        sorted_models = []

        # Add exact matches first
        for preferred in preferred_exact:
            if preferred in filtered_models:
                sorted_models.append(preferred)

        # Add partial matches (versioned models)
        for preferred in preferred_exact:
            matching = [
                m
                for m in filtered_models
                if m.startswith(preferred + "-") and m not in sorted_models
            ]
            matching.sort(reverse=True)  # Latest versions first
            sorted_models.extend(matching)

        # Add o1 models
        o1_models = [m for m in filtered_models if m.startswith("o1-")]
        o1_models.sort(reverse=True)
        sorted_models.extend(o1_models)

        # Add remaining models
        remaining = [m for m in filtered_models if m not in sorted_models]
        sorted_models.extend(sorted(remaining))

        return sorted_models[:15]  # Limit to top 15

    @staticmethod
    def get_anthropic_models() -> list[str]:
        """Get Anthropic models from litellm."""
        # Use litellm's Anthropic-specific model list
        anthropic_models = litellm.anthropic_models

        # Preferred order
        preferred_order = [
            "claude-3-5-sonnet",
            "claude-3-5-haiku",
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
        ]
        sorted_models = []

        for preferred in preferred_order:
            matching = [m for m in anthropic_models if preferred in m]
            matching.sort(reverse=True)  # Latest versions first
            sorted_models.extend(matching)

        # Add remaining models
        remaining = [m for m in anthropic_models if not any(p in m for p in preferred_order)]
        sorted_models.extend(sorted(remaining))

        return sorted_models[:15]  # Limit to top 15

    @staticmethod
    def get_gemini_models() -> list[str]:
        """Get Gemini models from litellm."""
        # Use litellm's Gemini-specific model list
        gemini_models = litellm.gemini_models

        # Preferred order
        preferred_order = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-2.0"]
        sorted_models = []

        for preferred in preferred_order:
            matching = [m for m in gemini_models if preferred in m]
            matching.sort(reverse=True)  # Latest versions first
            sorted_models.extend(matching)

        # Add remaining models
        remaining = [m for m in gemini_models if not any(p in m for p in preferred_order)]
        sorted_models.extend(sorted(remaining))

        return sorted_models[:15]  # Limit to top 15

    @staticmethod
    def get_openrouter_models() -> list[str]:
        """Get OpenRouter models from litellm."""
        # Use litellm's OpenRouter-specific model list
        openrouter_models = litellm.openrouter_models

        # Preferred models
        preferred_models = [
            "anthropic/claude-3-5-sonnet",
            "anthropic/claude-3-5-haiku",
            "openai/gpt-4o",
            "openai/gpt-4o-mini",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-8b-instruct",
        ]

        sorted_models = []
        for preferred in preferred_models:
            if preferred in openrouter_models:
                sorted_models.append(preferred)

        # Add remaining models from major providers
        remaining = [
            m
            for m in openrouter_models
            if m not in sorted_models
            and any(
                provider in m.lower()
                for provider in ["anthropic", "openai", "google", "meta-llama"]
            )
        ]
        sorted_models.extend(sorted(remaining))

        return sorted_models[:15]  # Limit to top 15
