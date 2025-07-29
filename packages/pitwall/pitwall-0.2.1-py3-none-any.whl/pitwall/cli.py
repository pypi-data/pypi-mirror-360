"""
Pitwall CLI - Command-line interface for the agentic AI companion for
MultiViewer
"""

import asyncio
from pathlib import Path
from typing import Optional
import requests

import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.prompt import Prompt
from rich.markdown import Markdown

from .pitwall import create_pitwall_agent, quick_analysis
from .memory import ConversationMemory


app = typer.Typer(
    name="pitwall",
    help="🏁 Pitwall - the agentic AI companion for MultiViewer, the best way"
    " to watch motorsport",
    no_args_is_help=False,
    invoke_without_command=True,
)
console = Console()

# Popular OpenRouter models for easy selection
POPULAR_MODELS = {
    "claude-sonnet": "anthropic/claude-sonnet-4",
    "claude-opus": "anthropic/claude-opus-4",
    "gpt-41": "openai/gpt-4.1",
    "gpt-41-mini": "openai/gpt-4.1-mini",
    "gemini-pro": "google/gemini-2.5-pro-preview",
    "gemini-flash": "google/gemini-2.5-flash-preview-05-20",
    "llama": "meta-llama/llama-4-maverick",
    "llama-free": "meta-llama/llama-4-maverick:free",
    "deepseek": "deepseek/deepseek-r1-0528",
}


def _check_multiviewer(url: str = "http://localhost:10101/graphql"):
    """Check if MultiViewer is running by testing GraphQL endpoint."""
    try:
        # Handle both full URLs and just the base URL
        check_url = url
        if url.endswith("/api/graphql"):
            check_url = url  # Already correct
        elif url.endswith("/graphql"):
            check_url = url.replace("/graphql", "/api/graphql")
        elif url.endswith("/"):
            check_url = url + "api/graphql"
        else:
            check_url = url + "/api/graphql"

        response = requests.get(check_url, timeout=2)
        success = response.status_code in [200, 400, 405]
        return success
    except requests.exceptions.RequestException:
        return False


@app.callback()
def main(
    ctx: typer.Context,
    model: str = typer.Option(
        "claude-sonnet",
        "--model",
        "-m",
        help="Model to use. Use shortcuts (claude-sonnet, gpt-4o, etc.) "
        "or full OpenRouter model names",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    session: Optional[str] = typer.Option(
        None, "--session", "-s", help="Resume a specific conversation session"
    ),
    url: str = typer.Option(
        "http://localhost:10101/graphql", "--url", "-u", help="MultiViewer instance URL"
    ),
    version: bool = typer.Option(False, "--version", help="Show version information"),
):
    """
    🏁 Pitwall - AI-powered motorsport data analysis

    Start an interactive chat session by running 'pitwall' with no arguments.
    Use specific commands for one-off analysis tasks.
    """
    # Handle version option
    if version:
        console.print()
        console.print(
            Panel.fit(
                "[bold blue]🏁 Pitwall[/bold blue]\n"
                "[dim]Version: 0.2.1[/dim]\n"
                "[dim]AI-powered motorsport data analysis[/dim]",
                border_style="blue",
            )
        )
        raise typer.Exit(0)

    if ctx.invoked_subcommand is None:
        # Default behavior: start chat
        # Check if MultiViewer is running
        if not _check_multiviewer(url):
            console.print(
                f"[bold red]Error:[/bold red] MultiViewer is not running at {url}"
            )
            console.print("Please start MultiViewer before using Pitwall")
            console.print("Download MultiViewer at: https://multiviewer.app")
            raise typer.Exit(1)

        resolved_model = _resolve_model(model)
        asyncio.run(_chat_async(resolved_model, verbose, session, multiviewer_url=url))


def _resolve_model(model: str) -> str:
    """Resolve model shortcuts to full OpenRouter model names."""
    return POPULAR_MODELS.get(model, model)


async def _chat_async(
    model: str,
    verbose: bool,
    session_id: Optional[str] = None,
    multiviewer_url: str = "http://localhost:10101/graphql",
):
    """Interactive chat session with the Pitwall agent."""

    # Welcome banner
    console.print()
    console.print(
        Panel.fit(
            "[bold blue]🏁 Welcome to Pitwall[/bold blue]\n"
            f"[dim]Using model: {model}[/dim]\n\n"
            "The agentic AI companion for MultiViewer.\n"
            "Ask me anything about the session you are currently watching with"
            " MultiViewer!\n\n"
            "[dim]Type 'exit', 'quit', or press Ctrl+C to end the session.[/dim]",
            border_style="blue",
            title="[bold]Pitwall Chat[/bold]",
        )
    )
    console.print()

    try:
        # Initialize memory
        memory = ConversationMemory()

        # Show session info if resuming
        if session_id:
            if memory.load_session(session_id):
                session_summary = memory.get_session_summary()
                console.print(f"[dim]📝 Resuming session: {session_id}")
                if session_summary:
                    msg_count = session_summary.get("message_count", 0)
                    console.print(f"[dim]💬 Messages: {msg_count}[/dim]")
                console.print()
            else:
                console.print(
                    f"[yellow]⚠️  Session {session_id} not found. "
                    "Starting new session.[/yellow]"
                )
                console.print()

        async with create_pitwall_agent(
            model=model,
            session_id=session_id,
            memory=memory,
            multiviewer_url=multiviewer_url,
        ) as agent:
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask(
                        "[bold green]You[/bold green]", console=console
                    )

                    # Check for exit commands
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        console.print("[dim]Goodbye! 🏁[/dim]")
                        break

                    if not user_input.strip():
                        continue

                    # Show thinking indicator
                    with Live(
                        Spinner("dots", text="Pitwall is thinking..."), console=console
                    ) as live:
                        try:
                            response = await agent.chat_turn(user_input)
                            live.stop()

                            # Display response with nice formatting
                            console.print()
                            console.print(
                                Panel(
                                    Markdown(response),
                                    title="[bold blue]🤖 Pitwall[/bold blue]",
                                    border_style="blue",
                                    padding=(1, 2),
                                )
                            )
                            console.print()

                        except Exception as e:
                            live.stop()
                            console.print(f"[bold red]Error:[/bold red] {e}")
                            console.print()

                except KeyboardInterrupt:
                    console.print("\n[dim]Goodbye! 🏁[/dim]")
                    break
                except EOFError:
                    console.print("\n[dim]Goodbye! 🏁[/dim]")
                    break

    except Exception as e:
        console.print(f"[bold red]Failed to initialize agent:[/bold red] {e}")
        raise typer.Exit(1)


@app.command()
def quick(
    query: str = typer.Argument(..., help="Quick analysis query"),
    model: str = typer.Option("claude-sonnet", "--model", "-m", help="Model to use"),
    url: str = typer.Option(
        "http://localhost:10101/graphql", "--url", "-u", help="MultiViewer instance URL"
    ),
):
    """
    Quick analysis for simple queries.

    Example:
        pitwall quick "Who won the last race?"
    """
    # Check if MultiViewer is running
    if not _check_multiviewer(url):
        console.print(
            f"[bold red]Error:[/bold red] MultiViewer is not running at {url}"
        )
        console.print("Please start MultiViewer before using Pitwall")
        console.print("Download MultiViewer at: https://multiviewer.app")
        raise typer.Exit(1)

    resolved_model = _resolve_model(model)
    asyncio.run(_quick_async(query, resolved_model, url))


async def _quick_async(query: str, model: str, multiviewer_url: str):
    """Async quick analysis execution."""
    with Live(Spinner("dots", text="Analyzing..."), console=console) as live:
        try:
            result = await quick_analysis(
                query, model=model, multiviewer_url=multiviewer_url
            )
            live.stop()

            console.print()
            console.print(
                Panel(
                    Markdown(result),
                    title="[bold green]⚡ Quick Result[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                )
            )

        except Exception as e:
            live.stop()
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)


@app.command()
def models():
    """Show available model shortcuts and their full names."""
    console.print()
    console.print(
        Panel(
            "\n".join(
                [
                    f"[bold green]{shortcut:<15}[/bold green] → [dim]{full_name}[/dim]"
                    for shortcut, full_name in POPULAR_MODELS.items()
                ]
            ),
            title="[bold blue]🤖 Available Model Shortcuts[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print(
        "\n[dim]You can also use any full OpenRouter model name directly.[/dim]"
    )


# Memory management subcommands
memory_app = typer.Typer(name="memory", help="🧠 Memory management commands")
app.add_typer(memory_app, name="memory")


@memory_app.command("list")
def list_sessions():
    """List all conversation sessions."""
    memory = ConversationMemory()
    sessions = memory.list_sessions()

    if not sessions:
        console.print("[dim]No conversation sessions found.[/dim]")
        return

    console.print()
    console.print("[bold blue]💬 Conversation Sessions[/bold blue]")
    console.print()

    for session in sessions:
        created = session.get("created_at", "Unknown")[:19].replace("T", " ")
        updated = session.get("updated_at", "Unknown")[:19].replace("T", " ")
        message_count = session.get("message_count", 0)
        model = session.get("model", "Unknown")

        console.print(f"[bold]{session['session_id'][:8]}...[/bold]")
        console.print(f"  [dim]Created: {created}[/dim]")
        console.print(f"  [dim]Updated: {updated}[/dim]")
        console.print(f"  [dim]Messages: {message_count} | Model: {model}[/dim]")
        console.print()


@memory_app.command("show")
def show_session(session_id: str = typer.Argument(..., help="Session ID to show")):
    """Show details of a specific conversation session."""
    memory = ConversationMemory()

    if not memory.load_session(session_id):
        console.print(f"[red]Session {session_id} not found.[/red]")
        raise typer.Exit(1)

    summary = memory.get_session_summary()
    context = memory.get_context_summary()

    if not summary:
        console.print("[red]Session summary not available.[/red]")
        raise typer.Exit(1)

    console.print()
    console.print(
        Panel(
            f"[bold]Session ID:[/bold] {summary['session_id']}\n"
            f"[bold]Created:[/bold] {summary['created_at'][:19].replace('T', ' ')}\n"
            f"[bold]Updated:[/bold] {summary['updated_at'][:19].replace('T', ' ')}\n"
            f"[bold]Model:[/bold] {summary['model']}\n"
            f"[bold]Messages:[/bold] {summary['message_count']}\n\n"
            f"{context}",
            title="[blue]Session Details[/blue]",
            border_style="blue",
        )
    )


@memory_app.command("delete")
def delete_session(
    session_id: str = typer.Argument(..., help="Session ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a conversation session."""
    memory = ConversationMemory()

    if not force:
        confirm = typer.confirm(f"Delete session {session_id}?")
        if not confirm:
            console.print("Cancelled.")
            return

    if memory.delete_session(session_id):
        console.print(f"[green]✓[/green] Session {session_id} deleted.")
    else:
        console.print(f"[red]Session {session_id} not found.[/red]")
        raise typer.Exit(1)


@memory_app.command("clear")
def clear_all_sessions(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Clear all conversation sessions."""
    memory = ConversationMemory()

    if not force:
        confirm = typer.confirm("Delete ALL conversation sessions?")
        if not confirm:
            console.print("Cancelled.")
            return

    memory.clear_all_sessions()
    console.print("[green]✓[/green] All sessions cleared.")


@memory_app.command("export")
def export_session(
    session_id: str = typer.Argument(..., help="Session ID to export"),
    output: str = typer.Option(
        "session.json", "--output", "-o", help="Output file path"
    ),
):
    """Export a conversation session to a file."""
    memory = ConversationMemory()
    output_path = Path(output)

    if memory.export_session(session_id, output_path):
        console.print(f"[green]✓[/green] Session exported to {output_path}")
    else:
        console.print(f"[red]Failed to export session {session_id}.[/red]")
        raise typer.Exit(1)


def cli_main():
    """Entry point for the CLI when installed as a package."""
    app()


if __name__ == "__main__":
    cli_main()
