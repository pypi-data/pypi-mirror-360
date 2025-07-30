# TicketPlease

CLI assistant for generating standardized task descriptions using AI.

![Demo](./images/tk-please-demo.gif)


## Overview

TicketPlease is a command-line tool that helps developers and engineers generate high-quality, standardized task descriptions for platforms like Jira and GitHub using AI. It provides an interactive flow to collect key requirements and produces formatted text ready to copy and paste.

## Features

- **Interactive Guided Flow**: Step-by-step questions to collect all necessary information, including multiline support for detailed task descriptions
- **AI-Powered Content Generation**: Uses LLMs to process user responses and generate complete, well-formatted descriptions
- **Multi-Platform Support**: Generates output in Markdown for GitHub or Jira text markup format
- **Configurable Setup**: Interactive wizard guides you through API key and AI model configuration when running `tk config` for the first time or if no configuration file exists
- **Persistent Preferences**: Saves user preferences for language, file paths, and platform
- **Iterative Refinement**: Allows users to request modifications to generated text
- **Multilingual Support**: Accepts input in user's language and generates output in configured language
- **Clipboard Integration**: Automatically copies final text to clipboard for immediate use

## LLM Model Configuration

TicketPlease leverages [LiteLLM](https://litellm.ai/) to provide a flexible and configurable way to interact with various Large Language Model (LLM) providers and models. This allows you to choose your preferred AI provider (e.g., OpenAI, Anthropic, Google, OpenRouter) and the specific model you wish to use.

During the `tk config` setup, you will be presented with a curated list of commonly used and supported models for your chosen provider. This list is dynamically fetched via LiteLLM.

**Custom Model Specification:**
If your desired model is supported by LiteLLM but does not appear in the default list provided during configuration, you can still specify it. Simply select the "Specify custom model" option (or similar, depending on the provider) in the wizard, and then manually enter the exact model name. TicketPlease will attempt to use this model via LiteLLM.

This flexibility ensures that you can always utilize the latest or most suitable LLM for your needs, even if it's not explicitly listed by default.

## Installation

### Prerequisites

- Python 3.10 or higher
- [asdf](https://asdf-vm.com/) for version management
- [Poetry](https://python-poetry.org/) for dependency management

### Installation using pip

```bash
pip install ticketplease
```

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/kcmr/ticket-please.git
cd ticket-please
```

2. Install Python and Poetry using asdf:
```bash
asdf install
```

3. Setup the development environment:
```bash
make setup
```

This will install all dependencies and set up pre-commit hooks automatically.

## Usage

### Basic Usage

| Type    | Command/Option       | Description                                     |
|:--------|:---------------------|:------------------------------------------------|
| Command | `tk please`          | Start the interactive task generation flow      |
| Command | `tk config`          | Configure your TicketPlease settings           |
| Command | `tk`                 | Show help (default behavior without arguments) |
| Option  | `tk --version`, `-v` | Show version and exit                           |
| Option  | `tk --help`          | Show this message and exit                      |

### Configuration

To configure TicketPlease, run the configuration command:

```bash
tk config
```

This will guide you through the setup process:

1. Choose your AI provider (OpenAI, Anthropic, Gemini, OpenRouter)
2. Enter your API key
3. Select an AI model
4. Configure default preferences

Once configured for the first time, you can update your preferences at any point by running `tk config` again. Additionally, many of these preferences (like output language or platform) can be overridden for individual tasks during the interactive task generation flow (`tk please`), providing maximum flexibility.

Configuration is stored in `~/.config/ticketplease/config.toml`.

After configuration, you can start creating tasks with `tk please`.

## Development

### Available Commands

```bash
# Setup development environment
make setup

# Install pre-commit hooks
make install-hooks

# Format code
make format

# Lint code
make lint

# Lint and fix code
make lint-fix

# Run tests
make test

# Run tests with coverage
make test-cov

# Run all checks (format, lint, test)
make check

# Clean build artifacts
make clean
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- **Code formatting**: Automatically formats code with ruff
- **Linting**: Checks code style and potential issues
- **Commit message validation**: Ensures commit messages follow conventional commits format
- **File checks**: Removes trailing whitespace, fixes end-of-file issues, etc.

Hooks are automatically installed when you run `make setup`. To manually install them:

```bash
make install-hooks
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the development checks: `make check`
5. Commit your changes using conventional commits
6. Push to your fork and create a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
