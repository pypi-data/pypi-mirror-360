"""Configuration management for TicketPlease."""

from pathlib import Path
from typing import Any

import toml


class Config:
    """Configuration manager for TicketPlease."""

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".config" / "ticketplease"
        self.config_file = self.config_dir / "config.toml"
        self._config: dict[str, Any] | None = None

    def load(self) -> dict[str, Any]:
        """Load configuration from file."""
        if self._config is None:
            if self.config_file.exists():
                self._config = toml.load(self.config_file)
            else:
                self._config = self._get_default_config()
        return self._config

    def save(self, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            toml.dump(config, f)
        self._config = config

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "api_keys": {
                "provider": "openai",
                "api_key": "",
            },
            "llm": {
                "model": "gpt-4o-mini",
            },
            "preferences": {
                "default_output_language": "es",
                "default_platform": "github",
                "default_ac_path": "",
                "default_dod_path": "",
            },
        }

    def get_api_key(self) -> str | None:
        """Get the API key from configuration."""
        config = self.load()
        return config.get("api_keys", {}).get("api_key")

    def get_provider(self) -> str:
        """Get the AI provider from configuration."""
        config = self.load()
        return config.get("api_keys", {}).get("provider", "openai")

    def get_model(self) -> str:
        """Get the LLM model from configuration."""
        config = self.load()
        return config.get("llm", {}).get("model", "gpt-4o-mini")

    def get_language(self) -> str:
        """Get the default output language."""
        config = self.load()
        return config.get("preferences", {}).get("default_output_language", "es")

    def get_platform(self) -> str:
        """Get the default platform."""
        config = self.load()
        return config.get("preferences", {}).get("default_platform", "github")  # noqa: E501

    def get_ac_path(self) -> str:
        """Get the default acceptance criteria path."""
        config = self.load()
        return config.get("preferences", {}).get("default_ac_path", "")

    def get_dod_path(self) -> str:
        """Get the default definition of done path."""
        config = self.load()
        return config.get("preferences", {}).get("default_dod_path", "")

    def is_configured(self) -> bool:
        """Check if the configuration is complete and valid."""
        config = self.load()
        api_key = config.get("api_keys", {}).get("api_key", "")
        provider = config.get("api_keys", {}).get("provider", "")
        model = config.get("llm", {}).get("model", "")

        return bool(api_key and provider and model)

    def is_first_run(self) -> bool:
        """Check if this is the first run (no config file exists)."""
        return not self.config_file.exists()
