"""
Suggestion management commands for human-in-the-loop verification
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from sqlmodel import Session

from .main import suggestions
from ..core.database import engine, create_db_and_tables
from ..services.suggestion_service import SuggestionService

console = Console()


@suggestions.command()
@click.option('--user-id', default=1, help='User ID (default: 1)')
@click.option('--limit', default=10, help='Number of suggestions to show (default: 10)')
def pending(user_id, limit):
    """
    Show pending suggestions that need human verification
    
    Example:
        goldfish suggestions pending --limit 5
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        suggestion_service = SuggestionService(db)
        pending_suggestions = suggestion_service.get_pending_suggestions(user_id)
        
        if not pending_suggestions:
            console.print("✅ No pending suggestions! All caught up.")
            return
        
        # Show limited results
        suggestions_to_show = pending_suggestions[:limit]
        
        table = Table(title=f"🤖 Pending AI Suggestions ({len(suggestions_to_show)} of {len(pending_suggestions)})", show_header=True)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Type", style="green", width=10)
        table.add_column("Entity", style="bold", width=20)
        table.add_column("Confidence", style="yellow", width=12)
        table.add_column("Context", style="dim", width=35)
        
        for suggestion in suggestions_to_show:
            confidence_str = f"{suggestion.confidence:.0%}"
            confidence_color = "green" if suggestion.confidence > 0.8 else "yellow" if suggestion.confidence > 0.6 else "red"
            
            table.add_row(
                str(suggestion.id),
                suggestion.entity_type.title(),
                suggestion.name,
                f"[{confidence_color}]{confidence_str}[/{confidence_color}]",
                suggestion.context[:32] + "..." if len(suggestion.context) > 35 else suggestion.context
            )
        
        console.print(table)
        
        if len(pending_suggestions) > limit:
            console.print(f"💡 Showing {limit} of {len(pending_suggestions)} suggestions. Use --limit to see more.")
        
        console.print("\n📋 Next steps:")
        console.print("• Review individual: [cyan]goldfish suggestions review <ID>[/cyan]")
        console.print("• Verify all: [cyan]goldfish suggestions verify-all[/cyan]")


@suggestions.command()
@click.argument('suggestion_id', type=int)
@click.option('--user-id', default=1, help='User ID (default: 1)')
def review(suggestion_id, user_id):
    """
    Review and verify a specific suggestion
    
    Example:
        goldfish suggestions review 1
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        suggestion_service = SuggestionService(db)
        
        # Get the suggestion
        from sqlmodel import select
        from ..models.suggested_entity import SuggestedEntity
        
        statement = select(SuggestedEntity).where(
            SuggestedEntity.id == suggestion_id,
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.status == "pending"
        )
        
        suggestion = db.exec(statement).first()
        if not suggestion:
            console.print(f"❌ Suggestion {suggestion_id} not found or already processed")
            return
        
        # Show detailed information
        _show_suggestion_details(suggestion)
        
        # Get user decision
        choice = Prompt.ask(
            "What would you like to do?",
            choices=["create", "link", "reject", "skip"],
            default="skip"
        )
        
        if choice == "create":
            try:
                entity_id = suggestion_service.confirm_suggestion(suggestion_id, user_id, create_new=True)
                console.print(f"✅ Created new {suggestion.entity_type} entity (ID: {entity_id})")
            except Exception as e:
                console.print(f"❌ Error creating entity: {e}")
        
        elif choice == "link":
            _handle_entity_linking(suggestion, suggestion_service, user_id)
        
        elif choice == "reject":
            try:
                suggestion_service.reject_suggestion(suggestion_id, user_id)
                console.print(f"❌ Suggestion rejected and marked for AI learning")
            except Exception as e:
                console.print(f"❌ Error rejecting suggestion: {e}")
        
        else:
            console.print("⏭️  Skipped suggestion")


@suggestions.command()
@click.option('--user-id', default=1, help='User ID (default: 1)')
@click.option('--auto-confirm-high', is_flag=True, help='Auto-confirm high confidence suggestions (>90%)')
def verify_all(user_id, auto_confirm_high):
    """
    Interactive verification of all pending suggestions
    
    Example:
        goldfish suggestions verify-all --auto-confirm-high
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        suggestion_service = SuggestionService(db)
        pending_suggestions = suggestion_service.get_pending_suggestions(user_id)
        
        if not pending_suggestions:
            console.print("✅ No pending suggestions! All caught up.")
            return
        
        console.print(f"📋 Processing {len(pending_suggestions)} suggestions...")
        
        confirmed = 0
        rejected = 0
        skipped = 0
        
        for i, suggestion in enumerate(pending_suggestions, 1):
            console.print(f"\n[bold]Suggestion {i}/{len(pending_suggestions)}[/bold]")
            
            # Auto-confirm high confidence if requested
            if auto_confirm_high and suggestion.confidence > 0.9:
                try:
                    suggestion_service.confirm_suggestion(suggestion.id, user_id, create_new=True)
                    confirmed += 1
                    console.print(f"✅ Auto-confirmed: {suggestion.name} ({suggestion.confidence:.0%} confidence)")
                    continue
                except Exception as e:
                    console.print(f"❌ Auto-confirm failed: {e}")
            
            # Show suggestion details
            _show_suggestion_details(suggestion)
            
            # Get user decision
            choice = Prompt.ask(
                "Action",
                choices=["create", "link", "reject", "skip", "quit"],
                default="skip"
            )
            
            if choice == "create":
                try:
                    suggestion_service.confirm_suggestion(suggestion.id, user_id, create_new=True)
                    confirmed += 1
                    console.print("✅ Created new entity!")
                except Exception as e:
                    console.print(f"❌ Error: {e}")
            
            elif choice == "link":
                if _handle_entity_linking(suggestion, suggestion_service, user_id):
                    confirmed += 1  # Count as confirmed since it was linked
                else:
                    skipped += 1
            
            elif choice == "reject":
                try:
                    suggestion_service.reject_suggestion(suggestion.id, user_id)
                    rejected += 1
                    console.print("❌ Rejected!")
                except Exception as e:
                    console.print(f"❌ Error: {e}")
            
            elif choice == "skip":
                skipped += 1
                console.print("⏭️  Skipped")
            
            elif choice == "quit":
                console.print("🛑 Stopping verification process")
                break
        
        # Summary
        summary_text = f"""
📊 Verification Summary:
• ✅ Confirmed: {confirmed}
• ❌ Rejected: {rejected}
• ⏭️  Skipped: {skipped}
• 🔄 Remaining: {len(pending_suggestions) - confirmed - rejected - skipped}
        """
        
        console.print(Panel(summary_text.strip(), title="Verification Complete", border_style="green"))


@suggestions.command()
@click.argument('note_id', type=int)
@click.option('--user-id', default=1, help='User ID (default: 1)')
def note(note_id, user_id):
    """
    Show suggestions for a specific note
    
    Example:
        goldfish suggestions note 123
    """
    create_db_and_tables()
    
    with Session(engine) as db:
        suggestion_service = SuggestionService(db)
        note_suggestions = suggestion_service.get_suggestions_by_note(note_id, user_id)
        
        if not note_suggestions:
            console.print(f"❌ No suggestions found for note {note_id}")
            return
        
        # Show status
        status = suggestion_service.get_confirmation_status(note_id, user_id)
        
        status_text = f"""
📄 Note {note_id} Status:
• Total suggestions: {status['total_suggestions']}
• ✅ Confirmed: {status['confirmed']}
• ❌ Rejected: {status['rejected']}
• ⏳ Pending: {status['pending']}
• Progress: {status['completion_percentage']:.1f}%
        """
        
        console.print(Panel(status_text.strip(), title="Note Status", border_style="blue"))
        
        # Show suggestions table
        table = Table(title=f"Suggestions for Note {note_id}", show_header=True)
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Type", style="green", width=10)
        table.add_column("Entity", style="bold", width=20)
        table.add_column("Status", style="yellow", width=12)
        table.add_column("Confidence", style="dim", width=12)
        
        for suggestion in note_suggestions:
            status_color = "green" if suggestion.status == "confirmed" else "red" if suggestion.status == "rejected" else "yellow"
            confidence_str = f"{suggestion.confidence:.0%}"
            
            table.add_row(
                str(suggestion.id),
                suggestion.entity_type.title(),
                suggestion.name,
                f"[{status_color}]{suggestion.status}[/{status_color}]",
                confidence_str
            )
        
        console.print(table)


def _show_suggestion_details(suggestion):
    """Show detailed information about a suggestion"""
    confidence_str = f"{suggestion.confidence:.0%}"
    confidence_color = "green" if suggestion.confidence > 0.8 else "yellow" if suggestion.confidence > 0.6 else "red"
    
    details_text = f"""
🤖 AI Suggestion Details:

• Type: {suggestion.entity_type.title()}
• Name: {suggestion.name}
• Confidence: [{confidence_color}]{confidence_str}[/{confidence_color}]
• Context: {suggestion.context}
• Original: {suggestion.ai_metadata.get('original_text', 'N/A')}
    """
    
    console.print(Panel(details_text.strip(), title=f"Suggestion #{suggestion.id}", border_style="blue"))


def _handle_entity_linking(suggestion, suggestion_service, user_id):
    """Handle entity linking workflow"""
    # Find existing entities
    existing_entities = suggestion_service.find_existing_entities(suggestion, limit=5)
    
    if not existing_entities:
        console.print("No existing entities found to link to", style="yellow")
        if Confirm.ask("Create new entity instead?", default=True):
            try:
                entity_id = suggestion_service.confirm_suggestion(suggestion.id, user_id, create_new=True)
                console.print(f"✅ Created new {suggestion.entity_type} entity (ID: {entity_id})")
                return True
            except Exception as e:
                console.print(f"❌ Error creating entity: {e}")
                return False
        return False
    
    # Show existing entities
    console.print("\n🔗 Found existing entities to link to:")
    
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
    
    console.print(table)
    
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
                console.print(f"Please enter a number between 0 and {max_choice}")
        except ValueError:
            console.print("Please enter a valid number")
    
    if choice_num == 0:
        # Create new entity
        try:
            entity_id = suggestion_service.confirm_suggestion(suggestion.id, user_id, create_new=True)
            console.print(f"✅ Created new {suggestion.entity_type} entity (ID: {entity_id})")
            return True
        except Exception as e:
            console.print(f"❌ Error creating entity: {e}")
            return False
    else:
        # Link to existing entity
        selected_entity = existing_entities[choice_num - 1]
        try:
            suggestion_service.confirm_suggestion(
                suggestion.id, 
                user_id, 
                create_new=False, 
                existing_entity_id=selected_entity["id"]
            )
            console.print(f"🔗 Linked to existing entity: {selected_entity['name']}")
            return True
        except Exception as e:
            console.print(f"❌ Error linking to entity: {e}")
            return False