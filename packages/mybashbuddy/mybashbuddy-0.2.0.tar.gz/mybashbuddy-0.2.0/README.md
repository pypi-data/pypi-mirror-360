# BashBuddy 🤖

> **Your AI-powered shell assistant and coding companion**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-bashbuddy-blue.svg)](https://pypi.org/project/bashbuddy/)

**BashBuddy** is a powerful command-line interface (CLI) tool that leverages Google's Gemini AI to transform your terminal experience. Whether you're a developer, system administrator, or tech enthusiast, BashBuddy helps you generate, understand, and fix commands and code with natural language.

##  Features

###  **Core Capabilities**
- **Generate** shell commands and code snippets from natural language descriptions
- **Explain** complex shell commands line by line
- **Fix** broken or incorrect shell commands
- **Explain Code** snippets in any programming language
- **Ask** anything - general knowledge, concepts, and explanations
- **Setup** interactive configuration for new users

###  **Advanced Features**
- **Multi-language Support**: Bash, Python, JavaScript, Java, C++, SQL, and more
- **Rich Output**: Beautiful, formatted responses with syntax highlighting
- **Clipboard Integration**: Copy results directly to clipboard
- **File Export**: Save generated code to files
- **Smart Explanations**: Get detailed explanations with examples

##  Installation

### Prerequisites
- Python 3.8 or higher
- [Google Gemini API key](https://aistudio.google.com/app/apikey)

### Quick Start

1. **Install from PyPI**
   ```bash
   pip install mybashbuddy
   ```

2. **Run the interactive setup**
   ```bash
   bb setup
   # or
   bashbuddy setup
   ```
   
   This will guide you through:
   - Getting your Gemini API key
   - Setting it up securely
   - Testing the connection

3. **Start using BashBuddy!**
   ```bash
   bb generate "List all Python files"
   bb ask "How do I use git?"
   # or
   bashbuddy generate "List all Python files"
   bashbuddy ask "How do I use git?"
   ```

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/bashbuddy.git
   cd BashBuddy
   ```

2. **Create and activate virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install BashBuddy in development mode**
   ```bash
   pip install -e .
   ```

5. **Set your Gemini API key**
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"
   
   # Windows (CMD)
   set GEMINI_API_KEY=your_api_key_here
   
   # Linux/macOS
   export GEMINI_API_KEY=your_api_key_here
   ```

##  Usage

### Basic Commands

```bash
# Generate a shell command
bb generate "List all Python files in the current directory" --lang bash --explain
# or
bashbuddy generate "List all Python files in the current directory" --lang bash --explain

# Explain a complex command
bb explain "find . -name '*.py' -exec grep -l 'import' {} \;"
# or
bashbuddy explain "find . -name '*.py' -exec grep -l 'import' {} \;"

# Fix a broken command
bb fix "ls -l | grpe py"
# or
bashbuddy fix "ls -l | grpe py"

# Explain code
bb explain-code "for i in range(10): print(i**2)"
# or
bashbuddy explain-code "for i in range(10): print(i**2)"

# Ask anything
bb ask "How do neural networks work?"
# or
bashbuddy ask "How do neural networks work?"

# Setup (for new users)
bb setup
# or
bashbuddy setup
```

### Advanced Usage

```bash
# Generate and save to file
bb generate "Create a web scraper" --lang python --save scraper.py --copy
# or
bashbuddy generate "Create a web scraper" --lang python --save scraper.py --copy

# Generate with explanation
bb generate "Backup all .py files with timestamp" --lang bash --explain
# or
bashbuddy generate "Backup all .py files with timestamp" --lang bash --explain

# Ask about current events
bb ask "What are the latest developments in AI technology?"
# or
bashbuddy ask "What are the latest developments in AI technology?"
```

##  Using BashBuddy as a Python Module

If the `bashbuddy` command is not recognized globally, you can use BashBuddy via Python's module system:

```sh
python -m bashbuddy.main --help
```

This will show the help menu and allow you to use all BashBuddy features, for example:

```sh
python -m bashbuddy.main generate "List all files" --lang bash --explain
python -m bashbuddy.main ask "What is quantum computing?"
```

**When to use this:**
- If the `bashbuddy` command is not found in your terminal.
- If you want to use BashBuddy in a virtual environment or from a local project install.
- If you are on Windows and don't want to edit your PATH or create a batch file.

##  Command Reference

### `generate` - Generate Commands and Code
Generate shell commands or code snippets from natural language descriptions.

```bash
bb generate "your task description" [OPTIONS]
# or
bashbuddy generate "your task description" [OPTIONS]
```

**Options:**
- `--lang <language>` - Specify programming language (bash, python, cpp, java, etc.)
- `--explain` - Add detailed explanation
- `--save <filename>` - Save result to file
- `--copy` - Copy result to clipboard

**Examples:**
```bash
bb generate "Create a backup script" --lang bash --explain
bb generate "Web scraper using requests" --lang python --save scraper.py
# or
bashbuddy generate "Create a backup script" --lang bash --explain
bashbuddy generate "Web scraper using requests" --lang python --save scraper.py
```

### `explain` - Explain Shell Commands
Get line-by-line explanations of shell commands.

```bash
bb explain "your shell command"
# or
bashbuddy explain "your shell command"
```

**Examples:**
```bash
bb explain "ls -la | grep py | wc -l"
bb explain "find . -name '*.py' -exec grep -l 'import' {} \;"
# or
bashbuddy explain "ls -la | grep py | wc -l"
bashbuddy explain "find . -name '*.py' -exec grep -l 'import' {} \;"
```

### `fix` - Fix Broken Commands
Fix and explain broken or incorrect shell commands.

```bash
bb fix "broken shell command"
# or
bashbuddy fix "broken shell command"
```

**Examples:**
```bash
bb fix "ls -l | grpe py"
bb fix "docker run -p 8000 myapp"
# or
bashbuddy fix "ls -l | grpe py"
bashbuddy fix "docker run -p 8000 myapp"
```

### `explain-code` - Explain Code Snippets
Get detailed explanations of code in any programming language.

```bash
bb explain-code "your code snippet"
# or
bashbuddy explain-code "your code snippet"
```

**Examples:**
```bash
bb explain-code "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
bb explain-code "async def fetch_data(): return await requests.get(url)"
# or
bashbuddy explain-code "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
bashbuddy explain-code "async def fetch_data(): return await requests.get(url)"
```

### `ask` - Ask Anything
Get answers and explanations on any topic.

```bash
bb ask "your question or topic"
# or
bashbuddy ask "your question or topic"
```

**Examples:**
```bash
bb ask "How do quantum computers work?"
bb ask "What are the benefits of renewable energy?"
bb ask "Explain the history of artificial intelligence"
# or
bashbuddy ask "How do quantum computers work?"
bashbuddy ask "What are the benefits of renewable energy?"
bashbuddy ask "Explain the history of artificial intelligence"
```

##  Use Cases

###  **System Administration**
```bash
# Generate monitoring scripts
bb generate "Monitor system resources and log to file" --lang bash

# Fix complex commands
bb fix "ps aux | grep python | awk '{print $2}' | xargs kill -9"
```

###  **Development**
```bash
# Generate API testing scripts
bb generate "Test REST API endpoints with curl" --lang bash

# Explain complex algorithms
bb explain-code "def quicksort(arr): return sorted(arr)"
```

###  **Data Processing**
```bash
# Generate data analysis scripts
bb generate "Process CSV files and create summary" --lang python

# Explain data commands
bb explain "cat data.csv | awk -F',' '{sum+=$3} END {print sum}'"
```

###  **Creative Projects**
```bash
# Generate games and utilities
bb generate "Create a number guessing game" --lang python

# Ask for inspiration
bb ask "What are some creative project ideas for beginners?"
```

##  Project Structure

```
BashBuddy/
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
└── bashbuddy/             # Main package
    ├── __init__.py
    ├── main.py            # CLI entry point
    ├── commands/          # Command modules
    │   ├── __init__.py
    │   ├── generate.py    # Generate command
    │   ├── explain.py     # Explain command
    │   ├── fix.py         # Fix command
    │   ├── explain_code.py # Explain code command
    │   └── ask.py         # Ask command
    └── core/              # Core functionality
        ├── __init__.py
        ├── llm.py         # Gemini API wrapper
        └── prompts.py     # Prompt templates
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY` - Your Google Gemini API key (required)

### API Key Setup
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable in your shell

## 🛠️ Troubleshooting

### Common Issues

#### 1. "GEMINI_API_KEY environment variable not set"
**Problem**: BashBuddy can't find your API key.

**Solutions**:
```bash
# Check your current setup
bb status

# Run the interactive setup
bb setup

# Or set manually for current session:
# Windows PowerShell:
$env:GEMINI_API_KEY="your_api_key_here"

# Windows CMD:
set GEMINI_API_KEY=your_api_key_here

# Linux/macOS:
export GEMINI_API_KEY=your_api_key_here
```

#### 2. API Key works in setup but not in commands
**Problem**: Environment variable isn't persisting between sessions.

**Solutions**:
- **Windows**: Use `bb setup` and choose option 3 (system environment variables)
- **PowerShell**: Use `bb setup` and choose option 2 (PowerShell profile)
- **Linux/macOS**: Add to your shell profile file (~/.bashrc, ~/.zshrc, etc.)
- **Alternative**: Create a `.env` file in your current directory

#### 3. "No compatible Gemini models found"
**Problem**: API key doesn't have access to Gemini models.

**Solutions**:
1. Check your API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Ensure you have access to Gemini models
3. Try regenerating your API key
4. Check your internet connection

#### 4. Command not found: bashbuddy
**Problem**: BashBuddy isn't installed or not in PATH.

**Solutions**:
```bash
# Reinstall BashBuddy
pip install --upgrade mybashbuddy

# Or use as Python module
python -m bashbuddy.main --help

# Check installation
pip show mybashbuddy
```

#### 5. Permission errors on Windows
**Problem**: Can't set environment variables due to permissions.

**Solutions**:
1. Run PowerShell as Administrator
2. Use `bb setup` and choose option 4 (.env file)
3. Set environment variables manually through System Properties

### Getting Help

1. **Check setup status**: `bb status`
2. **Reconfigure**: `bb setup`
3. **View help**: `bb --help`
4. **Report issues**: [GitHub Issues](https://github.com/Atharvadethe/BashBuddy/issues)

##  Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Powered by [Google Gemini](https://ai.google.dev/) AI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful output
- Icons by [Shields.io](https://shields.io/)

##  Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bashbuddy/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bashbuddy/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/bashbuddy/wiki)

---

<div align="center">
Made By Atharva Dethe
</div> 