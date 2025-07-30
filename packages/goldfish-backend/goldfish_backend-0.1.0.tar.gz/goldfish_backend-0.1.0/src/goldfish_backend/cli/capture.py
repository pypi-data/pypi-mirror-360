"""
Capture commands for quick text processing
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlmodel import Session

from .main import capture
from ..core.database import engine, create_db_and_tables
from ..services.entity_recognition import EntityRecognitionEngine
from ..services.suggestion_service import SuggestionService
from ..models.note import Note
from ..models.source_file import SourceFile
from ..models.user import User
from datetime import datetime

console = Console()


@capture.command()
@click.argument('text', required=True)
@click.option('--user-id', default=1, help='User ID (default: 1)')
@click.option('--preview', is_flag=True, help='Preview entities without storing')
def quick(text, user_id, preview):
    """
    Quick capture text with AI entity recognition
    
    Example:
        goldfish capture quick "TODO: Follow up with @sarah about #bloomberg-integration"
    """
    if preview:
        _preview_entities(text)
    else:
        _process_and_store(text, user_id)


@capture.command()
@click.argument('text', required=True)
def analyze(text):
    """
    Analyze text and show extracted entities (preview only)
    
    Example:
        goldfish capture analyze "Meeting with @john about #ai-platform project"
    """
    _preview_entities(text)


def _preview_entities(text):
    """Preview entities without storing in database"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task("Analyzing text with AI...", total=None)
        
        recognition_engine = EntityRecognitionEngine()
        result = recognition_engine.process_text(text)
    
    # Create summary table
    table = Table(title="🧠 AI Analysis Results", show_header=True)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Entity", style="green", width=25)
    table.add_column("Confidence", style="yellow", width=12)
    table.add_column("Context", style="dim", width=40)
    
    # Add entities
    for entity_type, entities in result["entities"].items():
        for entity in entities:
            confidence_str = f"{entity.confidence:.0%}"
            confidence_color = "green" if entity.confidence > 0.8 else "yellow" if entity.confidence > 0.6 else "red"
            
            table.add_row(
                entity_type.rstrip('s').title(),
                entity.name,
                f"[{confidence_color}]{confidence_str}[/{confidence_color}]",
                entity.context[:37] + "..." if len(entity.context) > 40 else entity.context
            )
    
    # Add tasks
    for task in result["tasks"]:
        confidence_str = f"{task.confidence:.0%}"
        table.add_row(
            "Task",
            task.content[:22] + "..." if len(task.content) > 25 else task.content,
            f"[green]{confidence_str}[/green]",
            task.context[:37] + "..." if len(task.context) > 40 else task.context
        )
    
    if table.row_count > 0:
        console.print(table)
    else:
        console.print("❌ No entities or tasks found in the text")
    
    # Summary
    summary_text = f"""
📊 Summary:
• {result['total_entities']} entities found
• {result['total_tasks']} tasks extracted
• {len(result['entities']['people'])} people, {len(result['entities']['projects'])} projects, {len(result['entities']['topics'])} topics
    """
    
    console.print(Panel(summary_text.strip(), title="Analysis Summary", border_style="blue"))


def _process_and_store(text, user_id):
    """Process text and store in database with suggestions"""
    # Initialize database
    create_db_and_tables()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Processing with AI and storing...", total=None)
        
        with Session(engine) as db:
            # Get or create user
            user = db.get(User, user_id)
            if not user:
                console.print(f"❌ User with ID {user_id} not found. Run: goldfish config setup")
                return
            
            # Create quick capture source file
            source_file = _get_or_create_quick_capture_file(user_id, db)
            
            # Create note
            note = Note(
                user_id=user_id,
                source_file_id=source_file.id,
                content=text,
                content_hash="",
                snapshot_at=datetime.utcnow(),
                processing_metadata={
                    "source": "cli_quick_capture",
                    "captured_at": datetime.utcnow().isoformat()
                }
            )
            
            db.add(note)
            db.flush()
            
            # Process with AI
            progress.update(task, description="Extracting entities and creating suggestions...")
            
            recognition_engine = EntityRecognitionEngine()
            result = recognition_engine.process_text(text)
            
            # Create suggestions
            suggestion_service = SuggestionService(db)
            suggestions = suggestion_service.create_suggestions_from_text(
                text=text,
                note_id=note.id,
                user_id=user_id
            )
            
            db.commit()
    
    # Show results
    console.print(f"✅ Text captured and processed (Note ID: {note.id})")
    
    if suggestions:
        console.print(f"🤖 Created {len(suggestions)} AI suggestions for verification")
        console.print("📋 Run: [cyan]goldfish suggestions pending[/cyan] to review")
        
        # Show quick preview
        table = Table(title="Suggestions Created", show_header=True)
        table.add_column("Type", width=10)
        table.add_column("Entity", width=20)
        table.add_column("Confidence", width=12)
        
        for suggestion in suggestions[:5]:  # Show first 5
            confidence_str = f"{suggestion.confidence:.0%}"
            confidence_color = "green" if suggestion.confidence > 0.8 else "yellow"
            table.add_row(
                suggestion.entity_type.title(),
                suggestion.name,
                f"[{confidence_color}]{confidence_str}[/{confidence_color}]"
            )
        
        if len(suggestions) > 5:
            table.add_row("...", f"({len(suggestions) - 5} more)", "")
        
        console.print(table)
    else:
        console.print("✨ No AI suggestions needed - text processed directly")


def _get_or_create_quick_capture_file(user_id: int, db: Session) -> SourceFile:
    """Get or create a virtual source file for quick captures"""
    from sqlmodel import select
    
    statement = select(SourceFile).where(
        SourceFile.user_id == user_id,
        SourceFile.file_path == "virtual://quick_capture",
        SourceFile.is_deleted == False
    )
    
    source_file = db.exec(statement).first()
    
    if not source_file:
        source_file = SourceFile(
            user_id=user_id,
            file_path="virtual://quick_capture",
            relative_path="quick_capture",
            file_hash="virtual",
            file_size=0,
            last_modified=datetime.utcnow(),
            is_watched=False
        )
        db.add(source_file)
        db.flush()
    
    return source_file