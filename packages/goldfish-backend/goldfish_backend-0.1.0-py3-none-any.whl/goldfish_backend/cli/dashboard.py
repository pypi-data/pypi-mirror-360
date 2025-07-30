"""
Dashboard commands for viewing tasks, entities, and status
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from sqlmodel import Session, select, func

from .main import dashboard
from ..core.database import engine, create_db_and_tables
from ..models.user import User
from ..models.note import Note
from ..models.suggested_entity import SuggestedEntity
from ..models.person import Person
from ..models.project import Project
from ..models.topic import Topic

console = Console()


@dashboard.command()
@click.option('--user-id', default=1, help='User ID (default: 1)')
def status(user_id):
    """
    Show overall dashboard status
    
    Example:
        goldfish dashboard status
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        user = db.get(User, user_id)
        if not user:
            console.print(f"❌ User with ID {user_id} not found. Run: goldfish config setup")
            return
        
        # Welcome message
        console.print(f"🐠 Welcome back, {user.full_name}!")
        
        # Get statistics
        stats = _get_user_stats(db, user_id)
        
        # Create dashboard panels
        panels = []
        
        # Capture stats
        capture_stats = f"""
📝 Capture Activity:
• Notes captured: {stats['notes']}
• Total characters: {stats['total_chars']:,}
• Latest capture: {stats['latest_note']}
        """
        panels.append(Panel(capture_stats.strip(), title="Capture", border_style="green"))
        
        # AI suggestions
        ai_stats = f"""
🤖 AI Processing:
• Pending suggestions: {stats['pending_suggestions']}
• Confirmed entities: {stats['confirmed_entities']}
• Accuracy rate: {stats['accuracy_rate']:.1f}%
        """
        panels.append(Panel(ai_stats.strip(), title="AI Status", border_style="blue"))
        
        # Entities
        entity_stats = f"""
📊 Knowledge Base:
• People: {stats['people']}
• Projects: {stats['projects']}
• Topics: {stats['topics']}
        """
        panels.append(Panel(entity_stats.strip(), title="Entities", border_style="yellow"))
        
        # Show panels in columns
        console.print(Columns(panels, equal=True))
        
        # Show suggestions status
        if stats['pending_suggestions'] > 0:
            console.print(f"\n🔔 You have {stats['pending_suggestions']} pending suggestions")
            console.print("📋 Run: [cyan]goldfish suggestions pending[/cyan] to review")
        else:
            console.print("\n✅ All suggestions reviewed! Great work!")
        
        # Quick actions
        actions = """
🚀 Quick Actions:
• Capture text: goldfish capture quick "your text"
• Review suggestions: goldfish suggestions pending
• View entities: goldfish dashboard entities
• File help: goldfish --help
        """
        
        console.print(Panel(actions.strip(), title="Next Steps", border_style="cyan"))


@dashboard.command()
@click.option('--user-id', default=1, help='User ID (default: 1)')
@click.option('--type', 'entity_type', help='Filter by entity type (people, projects, topics)')
def entities(user_id, entity_type):
    """
    Show all entities in the knowledge base
    
    Example:
        goldfish dashboard entities --type people
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        user = db.get(User, user_id)
        if not user:
            console.print(f"❌ User with ID {user_id} not found")
            return
        
        if entity_type:
            _show_entities_by_type(db, user_id, entity_type)
        else:
            _show_all_entities(db, user_id)


@dashboard.command()
@click.option('--user-id', default=1, help='User ID (default: 1)')
@click.option('--limit', default=10, help='Number of notes to show (default: 10)')
def notes(user_id, limit):
    """
    Show recent notes
    
    Example:
        goldfish dashboard notes --limit 5
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        user = db.get(User, user_id)
        if not user:
            console.print(f"❌ User with ID {user_id} not found")
            return
        
        # Get recent notes
        statement = select(Note).where(
            Note.user_id == user_id,
            Note.is_deleted == False
        ).order_by(Note.created_at.desc()).limit(limit)
        
        notes = db.exec(statement).all()
        
        if not notes:
            console.print("📝 No notes found")
            console.print("💡 Try: goldfish capture quick 'Your first note'")
            return
        
        table = Table(title=f"Recent Notes (Latest {len(notes)})", show_header=True)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Content", style="white", width=50)
        table.add_column("Created", style="dim", width=20)
        table.add_column("Source", style="green", width=15)
        
        for note in notes:
            content_preview = note.content[:47] + "..." if len(note.content) > 50 else note.content
            source = note.processing_metadata.get('source', 'unknown') if note.processing_metadata else 'unknown'
            created = note.created_at.strftime('%Y-%m-%d %H:%M')
            
            table.add_row(
                str(note.id),
                content_preview,
                created,
                source
            )
        
        console.print(table)


def _get_user_stats(db: Session, user_id: int) -> dict:
    """Get user statistics for dashboard"""
    
    # Notes
    note_count = db.exec(select(func.count(Note.id)).where(Note.user_id == user_id)).one()
    
    # Characters
    total_chars = db.exec(select(func.sum(func.length(Note.content))).where(Note.user_id == user_id)).one() or 0
    
    # Latest note
    latest_note = db.exec(select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc()).limit(1)).first()
    latest_str = latest_note.created_at.strftime('%Y-%m-%d') if latest_note else 'Never'
    
    # Suggestions
    pending_suggestions = db.exec(select(func.count(SuggestedEntity.id)).where(
        SuggestedEntity.user_id == user_id,
        SuggestedEntity.status == "pending"
    )).one()
    
    confirmed_entities = db.exec(select(func.count(SuggestedEntity.id)).where(
        SuggestedEntity.user_id == user_id,
        SuggestedEntity.status == "confirmed"
    )).one()
    
    total_suggestions = db.exec(select(func.count(SuggestedEntity.id)).where(
        SuggestedEntity.user_id == user_id,
        SuggestedEntity.status.in_(["confirmed", "rejected"])
    )).one()
    
    accuracy_rate = (confirmed_entities / total_suggestions * 100) if total_suggestions > 0 else 0
    
    # Entities
    people_count = db.exec(select(func.count(Person.id)).where(Person.user_id == user_id)).one()
    projects_count = db.exec(select(func.count(Project.id)).where(Project.user_id == user_id)).one()
    topics_count = db.exec(select(func.count(Topic.id)).where(Topic.user_id == user_id)).one()
    
    return {
        'notes': note_count,
        'total_chars': total_chars,
        'latest_note': latest_str,
        'pending_suggestions': pending_suggestions,
        'confirmed_entities': confirmed_entities,
        'accuracy_rate': accuracy_rate,
        'people': people_count,
        'projects': projects_count,
        'topics': topics_count,
    }


def _show_all_entities(db: Session, user_id: int):
    """Show all entities grouped by type"""
    
    # People
    people = db.exec(select(Person).where(Person.user_id == user_id, Person.is_deleted == False)).all()
    if people:
        table = Table(title="👥 People", show_header=True)
        table.add_column("ID", width=6)
        table.add_column("Name", width=25)
        table.add_column("Importance", width=12)
        table.add_column("Email", width=25)
        
        for person in people:
            table.add_row(
                str(person.id),
                person.name,
                f"{person.importance_score:.1f}/10",
                person.email or "Not set"
            )
        console.print(table)
    
    # Projects
    projects = db.exec(select(Project).where(Project.user_id == user_id, Project.is_deleted == False)).all()
    if projects:
        table = Table(title="📁 Projects", show_header=True)
        table.add_column("ID", width=6)
        table.add_column("Name", width=25)
        table.add_column("Status", width=12)
        table.add_column("Priority", width=12)
        table.add_column("Deadline", width=15)
        
        for project in projects:
            deadline_str = project.deadline.strftime('%Y-%m-%d') if project.deadline else "Not set"
            status_color = "green" if project.status == "active" else "yellow"
            
            table.add_row(
                str(project.id),
                project.name,
                f"[{status_color}]{project.status}[/{status_color}]",
                f"{project.priority_score:.1f}/10",
                deadline_str
            )
        console.print(table)
    
    # Topics
    topics = db.exec(select(Topic).where(Topic.user_id == user_id, Topic.is_deleted == False)).all()
    if topics:
        table = Table(title="🧠 Topics", show_header=True)
        table.add_column("ID", width=6)
        table.add_column("Name", width=25)
        table.add_column("Category", width=15)
        table.add_column("Research Score", width=15)
        
        for topic in topics:
            table.add_row(
                str(topic.id),
                topic.name,
                topic.category or "Uncategorized",
                f"{topic.research_score:.1f}/10"
            )
        console.print(table)
    
    if not (people or projects or topics):
        console.print("📋 No entities found yet")
        console.print("💡 Capture some text to get started: goldfish capture quick 'Your text here'")


def _show_entities_by_type(db: Session, user_id: int, entity_type: str):
    """Show entities of a specific type"""
    
    if entity_type == "people":
        entities = db.exec(select(Person).where(Person.user_id == user_id, Person.is_deleted == False)).all()
        if entities:
            table = Table(title="👥 People", show_header=True)
            table.add_column("ID", width=6)
            table.add_column("Name", width=25)
            table.add_column("Importance", width=12)
            table.add_column("Email", width=25)
            table.add_column("Bio", width=30)
            
            for entity in entities:
                table.add_row(
                    str(entity.id),
                    entity.name,
                    f"{entity.importance_score:.1f}/10",
                    entity.email or "Not set",
                    entity.bio[:27] + "..." if entity.bio and len(entity.bio) > 30 else entity.bio or "Not set"
                )
            console.print(table)
    
    elif entity_type == "projects":
        entities = db.exec(select(Project).where(Project.user_id == user_id, Project.is_deleted == False)).all()
        if entities:
            table = Table(title="📁 Projects", show_header=True)
            table.add_column("ID", width=6)
            table.add_column("Name", width=25)
            table.add_column("Status", width=12)
            table.add_column("Priority", width=12)
            table.add_column("Deadline", width=15)
            table.add_column("Description", width=30)
            
            for entity in entities:
                deadline_str = entity.deadline.strftime('%Y-%m-%d') if entity.deadline else "Not set"
                status_color = "green" if entity.status == "active" else "yellow"
                desc = entity.description[:27] + "..." if entity.description and len(entity.description) > 30 else entity.description or "Not set"
                
                table.add_row(
                    str(entity.id),
                    entity.name,
                    f"[{status_color}]{entity.status}[/{status_color}]",
                    f"{entity.priority_score:.1f}/10",
                    deadline_str,
                    desc
                )
            console.print(table)
    
    elif entity_type == "topics":
        entities = db.exec(select(Topic).where(Topic.user_id == user_id, Topic.is_deleted == False)).all()
        if entities:
            table = Table(title="🧠 Topics", show_header=True)
            table.add_column("ID", width=6)
            table.add_column("Name", width=25)
            table.add_column("Category", width=15)
            table.add_column("Research Score", width=15)
            table.add_column("Description", width=30)
            
            for entity in entities:
                desc = entity.description[:27] + "..." if entity.description and len(entity.description) > 30 else entity.description or "Not set"
                
                table.add_row(
                    str(entity.id),
                    entity.name,
                    entity.category or "Uncategorized",
                    f"{entity.research_score:.1f}/10",
                    desc
                )
            console.print(table)
    
    else:
        console.print(f"❌ Unknown entity type: {entity_type}")
        console.print("💡 Available types: people, projects, topics")
        return
    
    if not entities:
        console.print(f"📋 No {entity_type} found yet")
        console.print("💡 Capture some text to get started: goldfish capture quick 'Your text here'")