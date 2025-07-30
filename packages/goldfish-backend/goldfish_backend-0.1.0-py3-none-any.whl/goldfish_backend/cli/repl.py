"""
Interactive REPL mode for Goldfish CLI
"""
import os
import sys
from typing import Optional, List
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.columns import Columns
from sqlmodel import Session
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from ..core.database import engine, create_db_and_tables
from ..services.entity_recognition import EntityRecognitionEngine
from ..services.suggestion_service import SuggestionService
from ..models.note import Note
from ..models.source_file import SourceFile
from ..models.user import User
from .. import __version__

console = Console()


class GoldfishREPL:
    """Interactive REPL for Goldfish"""
    
    def __init__(self):
        self.console = console
        self.user_id = 1  # Default user
        self.user = None
        self.recognition_engine = EntityRecognitionEngine()
        self.running = True
        self.commands = {
            'help': self.show_help,
            'h': self.show_help,
            '?': self.show_help,
            'exit': self.exit_repl,
            'quit': self.exit_repl,
            'q': self.exit_repl,
            'status': self.show_status,
            's': self.show_status,
            'clear': self.clear_screen,
            'cls': self.clear_screen,
            'config': self.show_config,
            'entities': self.show_entities,
            'e': self.show_entities,
            'notes': self.show_notes,
            'n': self.show_notes,
        }
        
        # Setup prompt toolkit
        self.completer = WordCompleter(
            list(self.commands.keys()) + ['help', 'exit', 'status', 'clear'],
            ignore_case=True
        )
        
        # Create prompt session with history
        history_file = os.path.expanduser("~/.goldfish_history")
        self.session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
            complete_while_typing=True,
        )
        
    def start(self):
        """Start the interactive REPL"""
        # Initialize database
        create_db_and_tables()
        
        # Check if user exists
        with Session(engine) as db:
            self.user = db.get(User, self.user_id)
            if not self.user:
                self._first_time_setup()
            else:
                self.clear_screen()
        
        # Check for pending suggestions
        self._check_pending_suggestions()
        
        # Main REPL loop
        while self.running:
            try:
                self._process_input()
            except KeyboardInterrupt:
                self.console.print("\n💡 Use 'exit' or 'quit' to leave Goldfish")
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")
    
    def _check_pending_suggestions(self):
        """Check for pending suggestions and prompt to review"""
        with Session(engine) as db:
            suggestion_service = SuggestionService(db)
            pending = suggestion_service.get_pending_suggestions(self.user_id)
            
            if pending:
                self.console.print(f"\n🔔 You have {len(pending)} pending entity suggestions")
                if Confirm.ask("Review them now?", default=False):
                    self._verify_suggestions(pending, db)
    
    def _show_welcome(self):
        """Show welcome message"""
        title = Text("🐠 Goldfish Interactive Mode", style="bold blue")
        welcome_text = f"""
Welcome back, {self.user.full_name}!

Goldfish v{__version__} - AI-First Personal Knowledge Management

Quick Commands:
• Just type any text to capture it with AI processing
• 'help' or '?' - Show all commands
• 'status' or 's' - Show dashboard
• 'exit' or 'q' - Exit Goldfish

Start typing to capture a thought...
        """
        
        panel = Panel(
            welcome_text.strip(),
            title=title,
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def _first_time_setup(self):
        """First time setup wizard"""
        self.console.print(Panel("🐠 Welcome to Goldfish! Let's set up your account.", style="bold blue"))
        
        # Direct setup implementation to avoid recursion
        self.console.print("\n👤 Let's create your user account:")
        
        email = Prompt.ask("Email address")
        full_name = Prompt.ask("Full name")
        
        # Password with validation
        from ..core.auth import get_password_hash, validate_password_strength
        
        while True:
            password = Prompt.ask("Password", password=True)
            if validate_password_strength(password):
                break
            self.console.print("❌ Password must be at least 8 characters with uppercase, lowercase, digit, and special character")
        
        bio = Prompt.ask("Bio (optional)", default="")
        
        # Create user in database
        with Session(engine) as db:
            # Check if user already exists
            from sqlmodel import select
            existing_user = db.exec(select(User).where(User.email == email)).first()
            
            if existing_user:
                self.console.print(f"❌ User with email {email} already exists!")
                # Use the existing user
                self.user = existing_user
                self.user_id = existing_user.id
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
            
            self.user = user
            self.user_id = user.id
            
            self.console.print(f"✅ User account created! (ID: {user.id})")
        
        # Show next steps
        next_steps = """
🎉 Setup Complete!

You're now in interactive mode. Just start typing to capture thoughts!

Quick tips:
• Type any text to capture it with AI processing
• Use 'help' or '?' to see commands
• Use 'exit' or 'q' to quit
        """
        
        self.console.print(Panel(next_steps.strip(), title="Ready to Use!", border_style="green"))
    
    def _process_input(self):
        """Process user input"""
        try:
            # Use prompt_toolkit for better input handling
            user_input = self.session.prompt(
                '🐠 ',
                multiline=False,
            ).strip()
            
            if not user_input:
                return
            
            # Check if it's a command
            if user_input.lower() in self.commands:
                self.commands[user_input.lower()]()
            else:
                # Treat as text to capture
                self._capture_text(user_input)
        except EOFError:
            # Handle Ctrl+D
            self.exit_repl()
    
    def _capture_text(self, text: str):
        """Capture text with AI processing"""
        # First, analyze the text
        self.console.print("🤖 Analyzing with AI...", style="dim")
        result = self.recognition_engine.process_text(text)
        
        # Show what was found
        if result['total_entities'] > 0 or result['total_tasks'] > 0:
            self._show_analysis_results(result, text)
            
            # Ask if user wants to save
            if Confirm.ask("\n💾 Save this capture?", default=True):
                self._save_capture(text, result)
        else:
            # No entities found, just save as note
            if Confirm.ask("No entities found. Save as a simple note?", default=True):
                self._save_simple_note(text)
    
    def _show_analysis_results(self, result, text):
        """Show AI analysis results"""
        panels = []
        
        # Entities panel
        if result['total_entities'] > 0:
            entity_lines = []
            for entity_type, entities in result['entities'].items():
                if entities:
                    entity_lines.append(f"[bold]{entity_type.title()}:[/bold]")
                    for entity in entities:
                        confidence_color = "green" if entity.confidence > 0.8 else "yellow"
                        entity_lines.append(f"  • {entity.name} [{confidence_color}]{entity.confidence:.0%}[/{confidence_color}]")
            
            entities_panel = Panel(
                "\n".join(entity_lines),
                title="📊 Entities Found",
                border_style="green"
            )
            panels.append(entities_panel)
        
        # Tasks panel
        if result['tasks']:
            task_lines = []
            for task in result['tasks']:
                task_preview = task.content[:50] + "..." if len(task.content) > 50 else task.content
                task_lines.append(f"• {task_preview}")
            
            tasks_panel = Panel(
                "\n".join(task_lines),
                title="✅ Tasks Extracted",
                border_style="yellow"
            )
            panels.append(tasks_panel)
        
        # Show panels
        if panels:
            self.console.print(Columns(panels, equal=True))
    
    def _save_capture(self, text: str, result):
        """Save capture with AI suggestions"""
        with Session(engine) as db:
            # Create source file
            source_file = self._get_or_create_quick_capture_file(self.user_id, db)
            
            # Create note
            note = Note(
                user_id=self.user_id,
                source_file_id=source_file.id,
                content=text,
                content_hash="",
                snapshot_at=datetime.utcnow(),
                processing_metadata={
                    "source": "cli_interactive",
                    "captured_at": datetime.utcnow().isoformat()
                }
            )
            
            db.add(note)
            db.flush()
            
            # Create suggestions
            suggestion_service = SuggestionService(db)
            suggestions = suggestion_service.create_suggestions_from_text(
                text=text,
                note_id=note.id,
                user_id=self.user_id
            )
            
            db.commit()
            
            self.console.print(f"\n✅ Captured! (Note #{note.id})")
            
            # If there are suggestions, start verification flow
            if suggestions:
                self.console.print(f"📋 {len(suggestions)} entities need verification\n")
                if Confirm.ask("Verify entities now?", default=True):
                    self._verify_suggestions(suggestions, db)
    
    def _verify_suggestions(self, suggestions, db):
        """Interactive verification of suggestions"""
        suggestion_service = SuggestionService(db)
        confirmed = 0
        rejected = 0
        linked = 0
        
        for i, suggestion in enumerate(suggestions, 1):
            self.console.print(f"\n[bold]Entity {i}/{len(suggestions)}[/bold]")
            
            # Show suggestion details
            confidence_color = "green" if suggestion.confidence > 0.8 else "yellow"
            self.console.print(f"Type: {suggestion.entity_type.title()}")
            self.console.print(f"Name: [bold]{suggestion.name}[/bold]")
            self.console.print(f"Confidence: [{confidence_color}]{suggestion.confidence:.0%}[/{confidence_color}]")
            self.console.print(f"Context: [dim]{suggestion.context}[/dim]")
            
            # Find existing entities that could match
            existing_entities = suggestion_service.find_existing_entities(suggestion, limit=5)
            
            # Get decision
            choices = ["create", "c", "link", "l", "reject", "r", "skip", "s"]
            choice = Prompt.ask(
                "\nAction (create/c, link/l, reject/r, skip/s)",
                choices=choices,
                default="s"
            )
            
            if choice in ["create", "c"]:
                try:
                    suggestion_service.confirm_suggestion(suggestion.id, self.user_id, create_new=True)
                    confirmed += 1
                    self.console.print("✅ Created new entity!", style="green")
                except Exception as e:
                    self.console.print(f"❌ Error: {e}", style="red")
            
            elif choice in ["link", "l"]:
                # Show existing entities for linking
                if existing_entities:
                    self._show_entity_linking_options(suggestion, existing_entities, suggestion_service)
                    linked += 1
                else:
                    self.console.print("No existing entities found to link to", style="yellow")
                    # Ask if they want to create new instead
                    if Confirm.ask("Create new entity instead?", default=True):
                        try:
                            suggestion_service.confirm_suggestion(suggestion.id, self.user_id, create_new=True)
                            confirmed += 1
                            self.console.print("✅ Created new entity!", style="green")
                        except Exception as e:
                            self.console.print(f"❌ Error: {e}", style="red")
            
            elif choice in ["reject", "r"]:
                try:
                    suggestion_service.reject_suggestion(suggestion.id, self.user_id)
                    rejected += 1
                    self.console.print("❌ Rejected", style="red")
                except Exception as e:
                    self.console.print(f"❌ Error: {e}", style="red")
            
            else:
                self.console.print("⏭️  Skipped", style="yellow")
        
        # Summary
        self.console.print(f"\n📊 Verification complete: {confirmed} new, {linked} linked, {rejected} rejected")
    
    def _show_entity_linking_options(self, suggestion, existing_entities, suggestion_service):
        """Show existing entities for linking"""
        if not existing_entities:
            return
        
        self.console.print("\n🔗 Found existing entities to link to:")
        
        # Create a table of options
        from rich.table import Table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Name", style="white", width=25)
        table.add_column("Match", style="yellow", width=10)
        table.add_column("Details", style="dim", width=30)
        
        for i, entity in enumerate(existing_entities[:5], 1):
            match_color = "green" if entity["match_score"] > 0.8 else "yellow"
            match_text = f"[{match_color}]{entity['match_score']:.0%}[/{match_color}]"
            
            details = []
            if entity.get("aliases"):
                details.append(f"aliases: {', '.join(entity['aliases'][:2])}")
            if entity.get("status"):
                details.append(f"status: {entity['status']}")
            
            table.add_row(
                str(i),
                entity["name"],
                match_text,
                "; ".join(details) if details else ""
            )
        
        table.add_row("0", "Create new entity", "[green]100%[/green]", "New entity")
        
        self.console.print(table)
        
        # Get user choice
        max_choice = min(len(existing_entities), 5)
        while True:
            try:
                choice = Prompt.ask(
                    f"\nSelect entity to link to (0-{max_choice})",
                    default="0"
                )
                choice_num = int(choice)
                if 0 <= choice_num <= max_choice:
                    break
                else:
                    self.console.print(f"Please enter a number between 0 and {max_choice}")
            except ValueError:
                self.console.print("Please enter a valid number")
        
        if choice_num == 0:
            # Create new entity
            try:
                suggestion_service.confirm_suggestion(suggestion.id, self.user_id, create_new=True)
                self.console.print("✅ Created new entity!", style="green")
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")
        else:
            # Link to existing entity
            selected_entity = existing_entities[choice_num - 1]
            try:
                suggestion_service.confirm_suggestion(
                    suggestion.id, 
                    self.user_id, 
                    create_new=False, 
                    existing_entity_id=selected_entity["id"]
                )
                self.console.print(f"🔗 Linked to existing entity: {selected_entity['name']}", style="green")
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")
    
    def _save_simple_note(self, text: str):
        """Save a simple note without entities"""
        with Session(engine) as db:
            source_file = self._get_or_create_quick_capture_file(self.user_id, db)
            
            note = Note(
                user_id=self.user_id,
                source_file_id=source_file.id,
                content=text,
                content_hash="",
                snapshot_at=datetime.utcnow(),
                processing_metadata={
                    "source": "cli_interactive",
                    "captured_at": datetime.utcnow().isoformat()
                }
            )
            
            db.add(note)
            db.commit()
            
            self.console.print(f"✅ Note saved! (#{note.id})")
    
    def show_help(self):
        """Show help information"""
        help_text = """
🐠 Goldfish Interactive Commands

📝 Text Capture:
  Just type any text    Capture with AI entity extraction
  
📋 Commands:
  help, h, ?           Show this help
  status, s            Show dashboard status
  entities, e          Show all entities
  notes, n             Show recent notes
  config               Show configuration
  clear, cls           Clear screen
  exit, quit, q        Exit Goldfish
  
🔗 Entity Verification Options:
  create, c            Create new entity from suggestion
  link, l              Link to existing entity (shows candidates)
  reject, r            Reject suggestion (helps AI learn)
  skip, s              Skip for now (default)
  
💡 Tips:
  • Type naturally - AI will extract entities
  • Use @mentions for people
  • Use #hashtags for projects
  • Start with TODO: for tasks
  • Use 'link' to avoid duplicate entities
        """
        
        self.console.print(Panel(help_text.strip(), title="Help", border_style="blue"))
    
    def show_status(self):
        """Show dashboard status"""
        from ..cli.dashboard import _get_user_stats
        
        with Session(engine) as db:
            stats = _get_user_stats(db, self.user_id)
            
            # Create status panels
            panels = []
            
            # Activity
            activity = f"""📝 {stats['notes']} notes
📊 {stats['total_chars']:,} chars
🕐 {stats['latest_note']}"""
            panels.append(Panel(activity, title="Activity", border_style="green"))
            
            # AI Status
            ai_status = f"""🤖 {stats['pending_suggestions']} pending
✅ {stats['confirmed_entities']} confirmed
📈 {stats['accuracy_rate']:.1f}% accuracy"""
            panels.append(Panel(ai_status, title="AI Status", border_style="blue"))
            
            # Entities
            entities = f"""👥 {stats['people']} people
📁 {stats['projects']} projects
🧠 {stats['topics']} topics"""
            panels.append(Panel(entities, title="Knowledge Base", border_style="yellow"))
            
            self.console.print(Columns(panels, equal=True))
            
            if stats['pending_suggestions'] > 0:
                self.console.print(f"\n🔔 You have {stats['pending_suggestions']} pending suggestions")
    
    def show_entities(self):
        """Show entities summary"""
        from ..cli.dashboard import _show_all_entities
        
        with Session(engine) as db:
            _show_all_entities(db, self.user_id)
    
    def show_notes(self):
        """Show recent notes"""
        from ..cli.dashboard import notes
        
        # Create a mock context for the dashboard command
        import click
        ctx = click.Context(click.Command('notes'))
        ctx.params = {'user_id': self.user_id, 'limit': 5}
        
        with Session(engine) as db:
            from sqlmodel import select
            from ..models.note import Note
            
            statement = select(Note).where(
                Note.user_id == self.user_id,
                Note.is_deleted == False
            ).order_by(Note.created_at.desc()).limit(5)
            
            notes = db.exec(statement).all()
            
            if not notes:
                self.console.print("📝 No notes yet. Start typing to capture your first thought!")
                return
            
            table = Table(title="Recent Notes", show_header=True)
            table.add_column("ID", style="cyan", width=6)
            table.add_column("Content", style="white", width=60)
            table.add_column("Created", style="dim", width=16)
            
            for note in notes:
                content_preview = note.content[:57] + "..." if len(note.content) > 60 else note.content
                created = note.created_at.strftime('%Y-%m-%d %H:%M')
                
                table.add_row(
                    str(note.id),
                    content_preview,
                    created
                )
            
            self.console.print(table)
    
    def show_config(self):
        """Show configuration"""
        config_text = f"""
👤 User: {self.user.full_name}
📧 Email: {self.user.email}
🆔 User ID: {self.user_id}
📅 Member since: {self.user.created_at.strftime('%Y-%m-%d')}
        """
        
        self.console.print(Panel(config_text.strip(), title="Configuration", border_style="blue"))
    
    def clear_screen(self):
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self._show_welcome()
    
    def exit_repl(self):
        """Exit the REPL"""
        self.console.print("\n👋 Goodbye! Thanks for using Goldfish.")
        self.running = False
    
    def _get_or_create_quick_capture_file(self, user_id: int, db: Session) -> SourceFile:
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


# No longer need click import