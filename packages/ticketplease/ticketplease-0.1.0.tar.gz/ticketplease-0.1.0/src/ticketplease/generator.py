"""Task generation orchestrator for TicketPlease."""

from typing import Any

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from ai.service import AIService
from config.service import Config

from .collector import TaskDataCollector
from .utils import copy_to_clipboard

console = Console()


class TaskGenerator:
    """Orchestrates the complete task generation flow."""

    def __init__(self, config: Config) -> None:
        """Initialize the task generator."""
        self.config = config
        self.collector = TaskDataCollector(config)

    def generate_task(self) -> bool:
        """Execute the complete task generation flow."""
        try:
            # Check if configuration is valid
            if not self.config.is_configured():
                console.print(
                    "[red]❌ Configuration is incomplete. Please run 'tkp config' first.[/red]"
                )
                return False

            # Collect task data from user
            task_data = self.collector.collect_task_data()

            # Generate task description using AI
            ai_service = self._create_ai_service()
            description = self._generate_description(ai_service, task_data)

            if not description:
                console.print("[red]❌ Failed to generate task description.[/red]")
                return False

            # Show result and handle user actions
            return self._handle_result(ai_service, description)

        except KeyboardInterrupt:
            console.print("\n[yellow]❌ Task generation cancelled.[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]❌ Error during task generation: {e}[/red]")
            return False

    def _create_ai_service(self) -> AIService:
        """Create AI service instance from configuration."""
        provider = self.config.get_provider()
        api_key = self.config.get_api_key()
        model = self.config.get_model()

        if not api_key:
            raise ValueError("API key not found in configuration")

        return AIService(provider, api_key, model)

    def _generate_description(self, ai_service: AIService, task_data: dict[str, Any]) -> str:
        """Generate task description using AI service."""
        console.print("\n[bold blue]🤖 Generating task description...[/bold blue]")

        with console.status("[bold green]Thinking...", spinner="dots"):
            try:
                description = ai_service.generate_task_description(
                    task_description=task_data["task_description"],
                    acceptance_criteria=task_data["acceptance_criteria"],
                    definition_of_done=task_data["definition_of_done"],
                    platform=task_data["platform"],
                    language=task_data["language"],
                )
                return description.strip()
            except Exception as e:
                console.print(f"\n[red]❌ AI generation failed: {e}[/red]")
                return ""

    def _handle_result(self, ai_service: AIService, description: str) -> bool:
        """Handle the generated result and user actions."""
        while True:
            # Show the generated description
            self._display_result(description)

            # Ask user what to do next
            action = self._get_user_action()

            if action == "✅ Accept and copy to clipboard":
                return self._copy_and_finish(description)
            elif action == "🔄 Make changes":
                description = self._refine_description(ai_service, description)
                if not description:  # Refinement failed
                    return False
            elif action == "❌ Cancel":
                console.print("\n[yellow]Task generation cancelled.[/yellow]")
                return False

    def _display_result(self, description: str) -> None:
        """Display the generated task description."""
        console.print("\n" + "=" * 80)
        console.print(
            Panel.fit(
                "📋 Generated Task Description",
                title="[bold green]Result[/bold green]",
                border_style="green",
            )
        )
        console.print()

        # Display the content with markdown syntax highlighting and word wrapping
        syntax = Syntax(
            description, "markdown", theme="monokai", line_numbers=False, padding=2, word_wrap=True
        )
        console.print(syntax)
        console.print("\n" + "=" * 80)

    def _get_user_action(self) -> str | None:
        """Get user's choice for what to do with the result."""
        return questionary.select(
            "What would you like to do?",
            choices=[
                "✅ Accept and copy to clipboard",
                "🔄 Make changes",
                "❌ Cancel",
            ],
        ).ask()

    def _copy_and_finish(self, description: str) -> bool:
        """Copy description to clipboard and finish."""
        if copy_to_clipboard(description):
            console.print("\n[bold green]✅ Task description copied to clipboard![/bold green]")
            console.print("You can now paste it into your task management tool.")
        else:
            console.print(
                "\n[yellow]⚠️  Could not copy to clipboard, but here's your description:[/yellow]"
            )
            console.print("\n" + description)

        return True

    def _refine_description(self, ai_service: AIService, current_description: str) -> str:
        """Refine the current description based on user feedback."""
        refinement_request = questionary.text(
            "What would you like to change or add? (e.g., translate parts to another language)",
            validate=lambda x: bool(x.strip()) or "Refinement request cannot be empty",
        ).ask()

        if not refinement_request:
            return current_description

        console.print("\n[bold blue]🔄 Refining description...[/bold blue]")

        with console.status("[bold green]Thinking...", spinner="dots"):
            try:
                refined_description = ai_service.refine_task_description(
                    current_description, refinement_request.strip()
                )
                return refined_description.strip()
            except Exception as e:
                console.print(f"\n[red]❌ Refinement failed: {e}[/red]")
                console.print("Keeping the original description.")
                return current_description
