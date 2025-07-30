"""
Main CLI interface for Goldfish
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .. import __version__

console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.option('--no-interactive', is_flag=True, help='Disable interactive mode')
@click.pass_context
def cli(ctx, version, no_interactive):
    """
    🐠 Goldfish - AI-First Personal Knowledge Management
    
    Capture, organize, and retrieve your thoughts with AI assistance.
    """
    # Register subcommands on first call to avoid circular imports
    _register_subcommands()
    
    if version:
        console.print(f"Goldfish CLI v{__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        # Start interactive REPL mode
        if not no_interactive:
            try:
                from .repl import GoldfishREPL
                repl = GoldfishREPL()
                repl.start()
            except Exception as e:
                console.print(f"Error starting interactive mode: {e}")
                console.print("Use --no-interactive flag to use command mode")
                import traceback
                traceback.print_exc()
        else:
            # Show welcome message and available commands
            title = Text("🐠 Goldfish CLI", style="bold blue")
            welcome_text = f"""
Welcome to Goldfish v{__version__}!

An AI-first personal knowledge management system that helps you:
• Capture thoughts with natural language processing
• Extract entities (@people, #projects, topics) automatically  
• Verify AI suggestions through human-in-the-loop workflow
• Organize tasks with intelligent priority scoring

Get started with: goldfish capture "Your text here"
Or run: goldfish --help for all commands
            """
            
            panel = Panel(
                welcome_text.strip(),
                title=title,
                border_style="blue",
                padding=(1, 2)
            )
            console.print(panel)


@cli.group()
def capture():
    """Quick capture commands for text processing"""
    pass


@cli.group() 
def suggestions():
    """Manage AI entity suggestions"""
    pass


@cli.group()
def config():
    """Configuration and setup commands"""
    pass


@cli.group()
def dashboard():
    """View tasks, entities, and status"""
    pass


@cli.group()
def watch():
    """File watching and processing"""
    pass


# Import subcommands - done at the end to avoid circular imports
def _register_subcommands():
    """Register all subcommands to avoid circular imports"""
    from . import capture, suggestions, config, dashboard
    # No need to import anything explicitly - decorators register automatically
    pass


if __name__ == '__main__':
    _register_subcommands()
    cli()