# Bible CLI

A powerful command-line interface for Bible reading and study, designed specifically for programmers and terminal enthusiasts.

## Features

- 🔍 **Fast Search** - Full-text search with regex support and context
- 📖 **Multiple Translations** - Support for various Bible translations
- 🎨 **Rich Terminal UI** - Beautiful ASCII art and interactive TUI
- 🔖 **Bookmarks** - Save and organize your favorite verses
- 📊 **Reading History** - Track your Bible reading progress
- 🔧 **MCP Integration** - Model Context Protocol server for AI tools
- ⚙️ **Customizable** - Extensive configuration options
- 🎯 **Developer-Friendly** - Designed with programmers in mind

## Installation

### From PyPI (when published)

```bash
pip install bible-cli
# or
pipx install bible-cli
```

### From Source

```bash
git clone https://github.com/bible-cli/bible-cli
cd bible-cli
pip install -e .
```

### Using Poetry

```bash
git clone https://github.com/bible-cli/bible-cli
cd bible-cli
poetry install
poetry shell
```

## Quick Start

```bash
# Read a specific verse
bible read john 3:16

# Read a range of verses
bible read genesis 1:1-5

# Read an entire chapter
bible read psalms 23

# Search for verses
bible search "love your enemies"

# Interactive mode
bible

# Get help
bible --help
```

## Commands

### Reading Commands

- `bible read <book> <chapter>:<verse>` - Read specific verse(s)
- `bible goto <reference>` - Jump directly to a reference
- `bible random` - Display a random verse
- `bible daily` - Show verse of the day

### Search Commands

- `bible search <query>` - Search for words or phrases
  - `--exact` - Exact phrase matching
  - `--case-sensitive` - Case-sensitive search
  - `--book <name>` - Limit search to specific book
  - `--testament <old|new>` - Limit to testament
  - `--context <n>` - Show n verses of context
  - `--regex` - Use regex patterns

### Bookmark Commands

- `bible bookmarks` - List saved bookmarks
- `bible bookmark add <reference>` - Add bookmark
- `bible history` - Show reading history

### Interactive Mode

Launch the Terminal User Interface:

```bash
bible interactive
# or just
bible
```

#### Keyboard Shortcuts

- `j/k` or `↓/↑` - Navigate verses
- `h/l` or `←/→` - Previous/Next chapter
- `Space/b` - Page down/up
- `g` - Go to verse
- `/` - Search mode
- `r` - Random verse
- `m` - Bookmark current verse
- `?` - Help
- `q` - Quit

## MCP Server

Start the Model Context Protocol server for AI integration:

```bash
bible mcp serve --port 8000
```

### API Endpoints

- `GET /api/verse/{reference}` - Get specific verse
- `GET /api/search?q={query}` - Search verses
- `GET /api/books` - List all books
- `GET /api/random` - Get random verse
- `GET /api/context/{reference}` - Get verse with context
- `POST /api/export` - Export verses in various formats

## Configuration

Configuration file: `~/.config/bible-cli/config.toml`

```toml
[general]
default_translation = "NIV"
theme = "dark"
page_size = 10
show_verse_numbers = true

[ascii_art]
enabled = true
style = "simple"

[mcp]
enabled = false
endpoint = "http://localhost:8000"

[keybindings]
next_verse = ["j", "down"]
prev_verse = ["k", "up"]
search = ["/"]
```

## Data Sources

The application automatically downloads Bible data from:
- Basic Bible English (BBE) translation from [Open Bibles](https://github.com/seven1m/open-bibles)

Additional translations can be imported from:
- JSON Bible files
- USFX XML format
- Custom API endpoints

## Development

### Setup Development Environment

```bash
git clone https://github.com/bible-cli/bible-cli
cd bible-cli
poetry install
poetry shell
```

### Run Tests

```bash
pytest
pytest --cov=bible_cli
```

### Code Quality

```bash
black bible_cli/
ruff check bible_cli/
mypy bible_cli/
```

### Project Structure

```
bible-cli/
├── bible_cli/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Main entry point
│   ├── cli.py               # Click command definitions
│   ├── tui.py               # Textual TUI app
│   ├── models.py            # SQLAlchemy models
│   ├── search.py            # Search implementation
│   ├── mcp_server.py        # FastAPI MCP server
│   ├── config.py            # Configuration handling
│   ├── ascii_art.py         # ASCII art constants
│   ├── data_import.py       # Data import functionality
│   └── utils.py             # Helper functions
├── tests/                   # Test files
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## Examples

### Basic Usage

```bash
# Read John 3:16
bible read john 3:16

# Read Genesis 1:1-10
bible read genesis 1:1-10

# Search for verses about love
bible search love --testament new

# Search with context
bible search "faith without works" --context 2
```

### Advanced Search

```bash
# Exact phrase search
bible search "in the beginning" --exact

# Case-sensitive search
bible search "God" --case-sensitive

# Regex search
bible search "love.*neighbor" --regex

# Limit to specific book
bible search faith --book james
```

### Bookmarks and History

```bash
# Add bookmark
bible bookmark add "john 3:16" --name "God's Love"

# List bookmarks
bible bookmarks

# View reading history
bible history --limit 10
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests and linting
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bible data from [Open Bibles](https://github.com/seven1m/open-bibles)
- Built with [Click](https://click.palletsprojects.com/), [Textual](https://textual.textualize.io/), and [Rich](https://rich.readthedocs.io/)
- Inspired by the need for developer-friendly Bible study tools

## Support

- 🐛 [Report bugs](https://github.com/bible-cli/bible-cli/issues)
- 💡 [Request features](https://github.com/bible-cli/bible-cli/discussions)
- 📚 [Documentation](https://bible-cli.readthedocs.io/)
- 💬 [Community](https://github.com/bible-cli/bible-cli/discussions)