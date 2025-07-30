#!/usr/bin/env python3
"""Export Claude Code chat history to markdown.

ccexport is a minimal CLI tool that extracts conversation history from
Claude Code's local storage and exports it to clean markdown files.
"""

import json
from datetime import datetime
from pathlib import Path

import typer

__version__ = "0.1.1"

app = typer.Typer(
    name="ccexport",
    help="Export Claude Code chat history to markdown",
    add_completion=False,
)


def get_claude_project_path(cwd: Path) -> Path:
    """Transform current working directory to Claude project path."""
    # Convert path to string and replace / with -
    path_str = str(cwd.absolute())
    transformed = path_str.replace("/", "-").replace("_", "-")

    # Ensure single leading dash
    if not transformed.startswith("-"):
        transformed = "-" + transformed

    # Construct full path
    claude_base = Path.home() / ".claude" / "projects"
    return claude_base / transformed


def find_latest_session(project_path: Path) -> Path | None:
    """Find the most recently modified .jsonl file."""
    if not project_path.exists():
        return None

    jsonl_files = list(project_path.glob("*.jsonl"))
    if not jsonl_files:
        return None

    # Sort by modification time, most recent first
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


def extract_messages(session_file: Path) -> list[tuple[str, str]]:
    """Extract user and assistant messages from JSONL file."""
    messages = []

    with open(session_file, "r") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
                message = entry.get("message", {})
                role = message.get("role")

                if role == "user":
                    content = message.get("content", "")
                    # Handle both string and list content types
                    if isinstance(content, str) and content:
                        messages.append(("user", content))
                    # Skip array content (interrupted messages, tool results, etc.)

                elif role == "assistant":
                    # Extract only text content from assistant messages
                    content_items = message.get("content", [])
                    text_parts = []

                    for item in content_items:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text = item.get("text", "")
                            if text:
                                text_parts.append(text)

                    if text_parts:
                        messages.append(("assistant", "\n\n".join(text_parts)))

            except json.JSONDecodeError:
                # Skip malformed lines
                continue

    return messages


def export_to_markdown(messages: list[tuple[str, str]], output_path: Path) -> None:
    """Export messages to markdown file."""
    with open(output_path, "w") as f:
        for role, content in messages:
            if role == "user":
                f.write("---USER---\n")
            else:
                f.write("---ASSISTANT---\n")

            f.write(content)
            f.write("\n\n")


@app.command()
def main(
    path: Path = typer.Argument(
        default=Path.cwd(), help="Directory to export from", show_default="current directory"
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
        show_default="ccexport_YYYY-MM-DD_HHMMSS.md",
    ),
) -> None:
    """Export the latest Claude Code chat session to markdown."""

    # Get target directory
    target_dir = Path(path).expanduser().resolve()

    # Ensure the path exists and is a directory
    if not target_dir.exists():
        typer.echo(f"Error: Path '{target_dir}' does not exist.", err=True)
        raise typer.Exit(1)

    if not target_dir.is_dir():
        typer.echo(f"Error: Path '{target_dir}' is not a directory.", err=True)
        raise typer.Exit(1)

    # Transform to Claude project path
    project_path = get_claude_project_path(target_dir)

    # Find latest session
    session_file = find_latest_session(project_path)

    if not session_file:
        typer.echo("No Claude Code sessions found for this directory.", err=True)
        raise typer.Exit(1)

    # Extract messages
    messages = extract_messages(session_file)

    if not messages:
        typer.echo("No messages found in the session.", err=True)
        raise typer.Exit(1)

    # Determine output path
    if output is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output = Path(f"ccexport_{timestamp}.md")

    # Export to markdown
    export_to_markdown(messages, output)

    typer.echo(f"Exported {len(messages)} messages to {output}")


if __name__ == "__main__":
    app()
