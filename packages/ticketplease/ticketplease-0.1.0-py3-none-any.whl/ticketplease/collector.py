"""Data collection module for TicketPlease."""

from pathlib import Path
from typing import Any

import questionary
from rich.console import Console
from rich.panel import Panel

from config.service import Config

from .utils import read_file_content, validate_file_path

console = Console()


class TaskDataCollector:
    """Collects task data from user through interactive prompts."""

    def __init__(self, config: Config) -> None:
        """Initialize the task data collector."""
        self.config = config
        self.platforms = {
            "GitHub": "github",
            "Jira": "jira",
        }
        self.languages = {
            "English": "en",
            "Español": "es",
        }

    def collect_task_data(self) -> dict[str, Any]:
        """Collect all task data from user."""
        console.print()
        console.print(
            Panel.fit(
                "🎫 Let's create your task description!",
                title="[bold]Task Generation[/bold]",
                border_style="blue",
            )
        )
        console.print()

        # Collect basic task information
        task_description = self._collect_task_description()
        platform = self._collect_platform()
        language = self._collect_language()

        # Collect acceptance criteria
        acceptance_criteria = self._collect_acceptance_criteria()

        # Collect definition of done
        definition_of_done = self._collect_definition_of_done()

        return {
            "task_description": task_description,
            "platform": platform,
            "language": language,
            "acceptance_criteria": acceptance_criteria,
            "definition_of_done": definition_of_done,
        }

    def _collect_task_description(self) -> str:
        """Collect task description from user using multiline input."""
        task_description = self._collect_multiline_input()

        if not task_description:
            raise KeyboardInterrupt("Task generation cancelled")

        return task_description.strip()

    def _collect_multiline_input(self) -> str:
        """Collect multiline input from user using DONE keyword to finish."""
        while True:
            console.print("\n[bold]What needs to be done? (Describe the task in detail)[/bold]")
            console.print("[dim]• Enter your description (multiple lines supported)[/dim]")
            console.print("[dim]• Type 'DONE' on a new line to finish[/dim]")
            console.print("[dim]• Press Ctrl+C to cancel[/dim]")
            console.print()

            lines = []
            try:
                while True:
                    line = input()
                    if line.strip().upper() == "DONE":
                        break
                    lines.append(line)
            except KeyboardInterrupt:
                raise KeyboardInterrupt("Task generation cancelled") from None
            except EOFError:
                # Handle Ctrl+D gracefully
                console.print("\n[yellow]Input cancelled[/yellow]")
                raise KeyboardInterrupt("Task generation cancelled") from None

            result = "\n".join(lines).strip()

            if result:
                return result

            console.print("[red]Task description cannot be empty[/red]")

    def _collect_platform(self) -> str:
        """Collect target platform from user."""
        default_platform = self.config.get_platform()
        default_platform_display = self._get_platform_display_name(default_platform)

        platform_choice = questionary.select(
            "Target platform:",
            choices=list(self.platforms.keys()),
            default=default_platform_display,
        ).ask()

        if not platform_choice:
            raise KeyboardInterrupt("Task generation cancelled")

        return self.platforms[platform_choice]

    def _collect_language(self) -> str:
        """Collect output language from user."""
        default_language = self.config.get_language()
        default_language_display = self._get_language_display_name(default_language)

        language_choice = questionary.select(
            "Output language:",
            choices=list(self.languages.keys()),
            default=default_language_display,
        ).ask()

        if not language_choice:
            raise KeyboardInterrupt("Task generation cancelled")

        return self.languages[language_choice]

    def _collect_acceptance_criteria(self) -> list[str]:
        """Collect acceptance criteria from user."""
        console.print("\n[bold]Acceptance Criteria[/bold]")

        # Check if there's a default AC file
        default_ac_path = self.config.get_ac_path()
        if default_ac_path and validate_file_path(default_ac_path):
            use_file = questionary.confirm(
                f"Use default AC file ({Path(default_ac_path).name})?",
                default=True,
            ).ask()

            if use_file is None:
                raise KeyboardInterrupt("Task generation cancelled")

            if use_file:
                criteria = read_file_content(default_ac_path)
                if criteria:
                    console.print(f"✅ Loaded {len(criteria)} criteria from file")
                    return criteria

        # Manual input or file selection
        input_method = questionary.select(
            "How would you like to provide acceptance criteria?",
            choices=[
                "📝 Enter manually",
                "📁 Load from file",
                "🤖 Skip (AI will generate automatically)",
            ],
        ).ask()

        if not input_method:
            raise KeyboardInterrupt("Task generation cancelled")

        if input_method == "📝 Enter manually":
            return self._collect_criteria_manually("acceptance criteria")
        elif input_method == "📁 Load from file":
            return self._collect_criteria_from_file("acceptance criteria")
        else:  # Skip
            return []

    def _collect_definition_of_done(self) -> list[str]:
        """Collect definition of done from user."""
        console.print("\n[bold]Definition of Done[/bold]")

        # Check if there's a default DoD file
        default_dod_path = self.config.get_dod_path()
        if default_dod_path and validate_file_path(default_dod_path):
            use_file = questionary.confirm(
                f"Use default DoD file ({Path(default_dod_path).name})?",
                default=True,
            ).ask()

            if use_file is None:
                raise KeyboardInterrupt("Task generation cancelled")

            if use_file:
                dod_items = read_file_content(default_dod_path)
                if dod_items:
                    console.print(f"✅ Loaded {len(dod_items)} items from file")
                    return dod_items

        # Manual input or file selection
        input_method = questionary.select(
            "How would you like to provide definition of done?",
            choices=[
                "📝 Enter manually",
                "📁 Load from file",
                "🤖 Skip (AI will generate automatically)",
            ],
        ).ask()

        if not input_method:
            raise KeyboardInterrupt("Task generation cancelled")

        if input_method == "📝 Enter manually":
            return self._collect_criteria_manually("definition of done items")
        elif input_method == "📁 Load from file":
            return self._collect_criteria_from_file("definition of done")
        else:  # Skip
            return []

    def _collect_criteria_manually(self, criteria_type: str) -> list[str]:
        """Collect criteria manually from user input."""
        console.print(f"\nEnter {criteria_type} (one per line, empty line to finish):")
        criteria = []

        while True:
            try:
                item = questionary.text(
                    f"{len(criteria) + 1}. ",
                    validate=lambda x: True,  # Allow empty to finish
                ).ask()

                if item is None:
                    raise KeyboardInterrupt("Task generation cancelled")

                item = item.strip()
                if not item:  # Empty line means finish
                    break

                criteria.append(item)
            except KeyboardInterrupt:
                raise KeyboardInterrupt("Task generation cancelled") from None

        return criteria

    def _collect_criteria_from_file(self, criteria_type: str) -> list[str]:
        """Collect criteria from a file."""
        file_path = questionary.path(
            f"Path to {criteria_type} file:",
            validate=lambda x: self._validate_criteria_file(x),
            only_directories=False,
        ).ask()

        if not file_path:
            raise KeyboardInterrupt("Task generation cancelled")

        criteria = read_file_content(file_path)
        if criteria:
            console.print(f"✅ Loaded {len(criteria)} items from file")
        else:
            console.print("⚠️  File is empty or could not be read")

        return criteria

    def _validate_criteria_file(self, file_path: str) -> bool | str:
        """Validate criteria file path."""
        if not file_path or not file_path.strip():
            return "File path cannot be empty"

        if not validate_file_path(file_path):
            return f"File does not exist or is not readable: {file_path}"

        return True

    def _get_platform_display_name(self, platform: str) -> str:
        """Get display name for platform."""
        platform_map = {v: k for k, v in self.platforms.items()}
        return platform_map.get(platform, platform)

    def _get_language_display_name(self, language: str) -> str:
        """Get display name for language."""
        language_map = {v: k for k, v in self.languages.items()}
        return language_map.get(language, language)
