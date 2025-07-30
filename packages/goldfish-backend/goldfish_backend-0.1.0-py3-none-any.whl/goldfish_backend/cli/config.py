"""
Configuration and setup commands
"""
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from sqlmodel import Session

from .main import config
from ..core.database import engine, create_db_and_tables
from ..models.user import User
from ..core.auth import get_password_hash, validate_password_strength

console = Console()


@config.command()
def setup():
    """
    Initial setup wizard for Goldfish
    
    Creates user account and initializes database
    """
    console.print(Panel("🐠 Goldfish Setup Wizard", style="bold blue"))
    
    # Initialize database
    console.print("📦 Initializing database...")
    create_db_and_tables()
    console.print("✅ Database initialized")
    
    # Create user
    console.print("\n👤 Let's create your user account:")
    
    email = Prompt.ask("Email address")
    full_name = Prompt.ask("Full name")
    
    # Password with validation
    while True:
        password = Prompt.ask("Password", password=True)
        if validate_password_strength(password):
            break
        console.print("❌ Password must be at least 8 characters with uppercase, lowercase, digit, and special character")
    
    bio = Prompt.ask("Bio (optional)", default="")
    
    # Create user in database
    with Session(engine) as db:
        # Check if user already exists
        from sqlmodel import select
        existing_user = db.exec(select(User).where(User.email == email)).first()
        
        if existing_user:
            console.print(f"❌ User with email {email} already exists!")
            return
        
        # Create new user
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            bio=bio if bio else None
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        console.print(f"✅ User account created! (ID: {user.id})")
    
    # Show next steps
    next_steps = """
🎉 Setup Complete!

Next steps:
• Try quick capture: goldfish capture quick "Your text here"
• Analyze text: goldfish capture analyze "Meeting notes..."
• View dashboard: goldfish dashboard status
• Get help: goldfish --help
    """
    
    console.print(Panel(next_steps.strip(), title="Ready to Use!", border_style="green"))


@config.command()
@click.option('--user-id', default=1, help='User ID to show info for')
def info(user_id):
    """
    Show current configuration and user info
    
    Example:
        goldfish config info --user-id 1
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        user = db.get(User, user_id)
        
        if not user:
            console.print(f"❌ User with ID {user_id} not found")
            console.print("💡 Run: goldfish config setup")
            return
        
        # Show user info
        user_info = f"""
👤 User Information:
• ID: {user.id}
• Email: {user.email}
• Name: {user.full_name}
• Bio: {user.bio or 'Not set'}
• Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
• Status: {'Active' if user.is_active else 'Inactive'}
        """
        
        console.print(Panel(user_info.strip(), title="Configuration", border_style="blue"))
        
        # Show database stats
        from ..models.note import Note
        from ..models.suggested_entity import SuggestedEntity
        from sqlmodel import select, func
        
        note_count = db.exec(select(func.count(Note.id)).where(Note.user_id == user_id)).one()
        suggestion_count = db.exec(select(func.count(SuggestedEntity.id)).where(
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.status == "pending"
        )).one()
        
        stats_info = f"""
📊 Database Stats:
• Notes captured: {note_count}
• Pending suggestions: {suggestion_count}
• Database location: goldfish.db
        """
        
        console.print(Panel(stats_info.strip(), title="Statistics", border_style="green"))


@config.command()
@click.option('--user-id', default=1, help='User ID to update')
def update(user_id):
    """
    Update user configuration
    
    Example:
        goldfish config update --user-id 1
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        user = db.get(User, user_id)
        
        if not user:
            console.print(f"❌ User with ID {user_id} not found")
            return
        
        console.print(f"📝 Updating user: {user.email}")
        
        # Update fields
        new_name = Prompt.ask("Full name", default=user.full_name)
        new_bio = Prompt.ask("Bio", default=user.bio or "")
        
        # Update user
        user.full_name = new_name
        user.bio = new_bio if new_bio else None
        
        db.add(user)
        db.commit()
        
        console.print("✅ User updated successfully!")


@config.command()
def reset():
    """
    Reset database (WARNING: This will delete all data!)
    """
    from rich.prompt import Confirm
    
    console.print("⚠️  [bold red]WARNING: This will delete ALL data![/bold red]")
    
    if not Confirm.ask("Are you absolutely sure you want to reset the database?"):
        console.print("❌ Reset cancelled")
        return
    
    if not Confirm.ask("This action cannot be undone. Continue?"):
        console.print("❌ Reset cancelled")
        return
    
    # Drop and recreate tables
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()
    
    console.print("🗑️  Database reset complete!")
    console.print("💡 Run: goldfish config setup to create a new user")