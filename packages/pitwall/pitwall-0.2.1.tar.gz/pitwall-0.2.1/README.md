# Pitwall 🏁

**The agentic AI companion to MultiViewer, the best app to watch motorsports**

Pitwall transforms your motorsport viewing experience by augmenting 
[MultiViewer](https://multiviewer.app)
with an agentic intelligence you can interrogate over the course of a racing
session.

[![CI](https://github.com/RobSpectre/pitwall/workflows/CI/badge.svg)](https://github.com/RobSpectre/pitwall/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/RobSpectre/pitwall/actions)
[![Coverage](https://img.shields.io/badge/coverage-66%25-yellow)](https://github.com/RobSpectre/pitwall)


### Key Features

- 💬 **Conversational Interface**: Ask questions, request specific views, or let Pitwall decide what to show
- 🤖 **AI-Powered Feed Management**: A conversational interface to control
  driver onboards, broadcast feeds, and more. 
- 🏎️ **Racing Intelligence**: Pit strategy, race control interpretation, and
  more. 
- 🧠 **Session Memory**: Remembers context and preferences throughout your viewing session
- 🌐 **Multi-Series Support**: Works with all motorsports series that MultiViewer supports
-    **OpenRouter Powered**: Use any of the thousands of LLMs on
     [OpenRouter](https://openrouter.ai)


## Quick Start

### Prerequisites

- Python 3.10 or higher
- [MultiViewer](https://multiviewer.app) installed and running
- A streaming subscription for the motorsport series you wish to watch. 
  - [F1TV](https://f1tv.formula1.com/)
  - [FIAWECTV](https://fiawec.tv/page/679a56921229db49627128a6)
  - [IndyCarLive](https://www.indycarlive.com/)
- OpenRouter API key for AI model access

### Installation

```bash
pip install pitwall
```

### Basic Usage

1. **Start MultiViewer** and ensure it's running on your system
2. **Set your API key**:
   ```bash
   export OPENROUTER_API_KEY="your-openrouter-api-key"
   ```
3. **Launch Pitwall**:
   ```bash
   pitwall
   ```

## Available Commands

### Main Commands

- **`pitwall`** - Start interactive chat mode (default)
- **`pitwall quick <query>`** - Quick analysis for simple queries
- **`pitwall models`** - Show available model shortcuts
- **`pitwall memory`** - Memory management commands
- **`pitwall --version`** - Show version information

### Memory Commands

- **`pitwall memory list`** - List all conversation sessions
- **`pitwall memory show <session-id>`** - Show details of a specific session
- **`pitwall memory export <session-id>`** - Export session to JSON file
- **`pitwall memory delete <session-id>`** - Delete a specific session
- **`pitwall memory clear`** - Clear all sessions

### Example Commands

```bash
# Quick analysis of current session
pitwall quick "What's the current battle for the lead?"

# Start interactive chat mode (default command)
pitwall

# Use a specific AI model
pitwall --model claude-sonnet

# Connect to remote MultiViewer instance
pitwall --url http://remote-server:10101/graphql

# Check available models
pitwall models

# Resume a previous session
pitwall --session your-session-id

# Quick analysis with specific model
pitwall quick "Who's leading?" --model gpt-41

# Quick analysis with remote MultiViewer
pitwall quick "Current standings" --url http://remote-server:10101/graphql
```


## Configuration

### Environment Variables

```bash
# Required: OpenRouter API key for AI models
export OPENROUTER_API_KEY="your-key-here"
```

### CLI Options

```bash
# Core options available for all commands
--model, -m     # AI model to use (see Model Options below)
--verbose, -v   # Enable verbose output
--session, -s   # Resume a specific conversation session
--url, -u       # MultiViewer instance URL (default: http://localhost:10101/graphql)
--version       # Show version information
```

### Model Options

Pitwall supports various AI models through OpenRouter:

- **claude-sonnet**: Anthropic Claude Sonnet 4 (recommended)
- **claude-opus**: Anthropic Claude Opus 4 (premium)
- **gpt-41**: OpenAI GPT-4.1
- **gpt-41-mini**: OpenAI GPT-4.1 Mini
- **gemini-pro**: Google Gemini 2.5 Pro Preview
- **gemini-flash**: Google Gemini 2.5 Flash Preview
- **llama**: Meta Llama 4 Maverick
- **llama-free**: Meta Llama 4 Maverick (free tier)
- **deepseek**: DeepSeek R1

You can also use any full OpenRouter model name directly.

## Advanced Features

### Remote MultiViewer Connections

Pitwall connects to MultiViewer instances using the `--url` option (defaults to localhost):

```bash
# Connect to a remote MultiViewer instance
pitwall --url http://192.168.1.100:10101/graphql

# Quick analysis with remote instance
pitwall quick "Current race status" --url http://remote-server:10101/graphql

# Use specific model with remote instance
pitwall --model claude-opus --url http://remote-server:10101/graphql

# Default behavior (connects to localhost)
pitwall
```

This is useful when:
- Running MultiViewer on a different machine
- Accessing a shared MultiViewer instance
- Using Pitwall from a remote location

### Session Memory

Pitwall remembers your viewing sessions:

```bash
# List previous sessions
pitwall memory list

# Show details of a specific session
pitwall memory show abc123

# Resume a specific session
pitwall --session abc123

# Export session data
pitwall memory export abc123 --output session.json

# Delete a session
pitwall memory delete abc123

# Clear all sessions
pitwall memory clear
```

## Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/RobSpectre/pitwall.git
cd pitwall

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting and formatting
black .
flake8
mypy .

# Run tests with coverage
pytest --cov

# Run tests across multiple Python versions
tox
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test files
pytest tests/test_cli.py
pytest tests/test_memory.py
pytest tests/test_pitwall.py

# Run tests with verbose output
pytest -v

# Run across multiple Python versions
tox

# Run specific tox environments
tox -e py310
tox -e py311
tox -e py312
tox -e lint
tox -e type-check
```

## Architecture

Pitwall is built with a modular architecture:

```
pitwall/
├── cli.py          # Command-line interface
├── pitwall.py      # Core AI agent logic
├── memory.py       # Session management
├── prompts.py      # AI prompt templates
└── __init__.py     # Package initialization
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Meta 

- Vibe-coded by [Rob Spectre](https://brooklynhacker.com)
- Released under [MIT License](https://opensource.org/license/mit)
- Software is as is - no warranty expressed or implied, diggity.
- This package is not developed or maintained by MultiViewer or any racing
  series
- 🏎️ Go Weeyums! 🏎️

## Acknowledgements

- [MultiViewer](https://multiviewer.app) for the incredible motorsport viewing platform
- [mvf1](https://github.com/RobSpectre/mvf1) for MultiViewer MCP support
- [PydanticAI](https://github.com/pydantic/pydantic-ai) for the AI agent framework

