# ccexport

Export Claude Code (cc) chat history to markdown format. A minimal CLI tool that extracts conversation history from Claude Code's local storage.

## Features

- Exports the most recent Claude Code session for any project
- Outputs clean markdown with only user/assistant messages
- Filters out tool calls, thinking blocks, and interrupted messages
- Handles special characters in directory names (underscores → dashes)
- No configuration needed - uses Claude's standard storage location (~/.claude)

## Installation

### Prerequisites

Make sure you have [uv](https://docs.astral.sh/uv/) installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Global Installation

Clone and install globally:

```bash
git clone https://github.com/odysseus0/ccexport.git
cd ccexport
uv tool install .
```

Then use from anywhere:
```bash
ccexport
```

### Development

Clone the repository:

```bash
git clone https://github.com/odysseus0/ccexport.git
cd ccexport
```

Run directly without installing:

```bash
# Using uv run (recommended)
uv run ccexport

# Or with arguments
uv run ccexport ~/projects/myapp -o session.md
```

Format and lint:

```bash
uv run --with ruff ruff check .
uv run --with ruff ruff format .
```

## Usage

Export Claude Code chat sessions:

```bash
# Export latest session from current directory
ccexport

# Export from a specific directory
ccexport /path/to/project

# Export to custom filename
ccexport -o my_session.md

# Export from specific directory to custom filename
ccexport /path/to/project -o my_session.md
```

The tool will:
1. Find your Claude Code sessions for the specified directory
2. Select the most recently modified session
3. Extract user and assistant messages (text only, skipping interrupted messages)
4. Export to a markdown file with timestamp-based filename

## Output Format

Messages are exported as simple markdown:

```markdown
## User
Your question here

## Assistant
Claude's response here

## User
Follow-up question

## Assistant
Follow-up response
```

