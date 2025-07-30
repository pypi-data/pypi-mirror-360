"""Interactive menu system for ENOUGH."""
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()

class Menu:
    """Interactive menu system."""
    
    def __init__(self):
        """Initialize the menu system."""
        self.console = Console()
        
    def display_main_menu(self) -> str:
        """Display the main menu and return the selected option."""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold blue]ENOUGH - A Mindful Journaling Tool[/bold blue]\n"
            "[dim]Your companion for self-reflection and growth[/dim]"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Description")
        
        options = [
            ("1", "Start Journaling Session"),
            ("2", "Review Past Entries"),
            ("3", "Manage Exercise Templates"),
            ("4", "View Progress & Stats"),
            ("5", "Settings"),
            ("q", "Quit")
        ]
        
        for opt, desc in options:
            table.add_row(f"[{opt}]", desc)
            
        self.console.print(table)
        
        choice = Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "q"],
            show_choices=False
        )
        
        return choice
        
    def display_journal_menu(self) -> Optional[str]:
        """Display available journal templates and return selected one."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Select Journal Template[/bold cyan]"))
        
        # Get available templates
        templates_dir = Path("Core/enough/data/templates")
        templates = list(templates_dir.glob("*.yaml"))
        
        if not templates:
            self.console.print("[yellow]No templates found![/yellow]")
            return None
            
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Template")
        
        for idx, template in enumerate(templates, 1):
            table.add_row(f"[{idx}]", template.stem)
            
        table.add_row("[b]", "Back to main menu")
        
        self.console.print(table)
        
        choice = Prompt.ask(
            "\nSelect template",
            choices=[str(i) for i in range(1, len(templates) + 1)] + ["b"],
            show_choices=False
        )
        
        if choice == "b":
            return None
            
        return str(templates[int(choice) - 1])
        
    def display_review_menu(self) -> Optional[str]:
        """Display review options menu."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Review Options[/bold cyan]"))
        
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Description")
        
        options = [
            ("1", "View Today's Entries"),
            ("2", "View This Week's Entries"),
            ("3", "View by Date"),
            ("4", "View by Tag"),
            ("5", "Export Entries"),
            ("b", "Back to Main Menu")
        ]
        
        for opt, desc in options:
            table.add_row(f"[{opt}]", desc)
            
        self.console.print(table)
        
        return Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "b"],
            show_choices=False
        )
        
    def display_template_menu(self) -> Optional[str]:
        """Display template management menu."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Template Management[/bold cyan]"))
        
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Description")
        
        options = [
            ("1", "Create New Template"),
            ("2", "Edit Existing Template"),
            ("3", "Delete Template"),
            ("4", "Import Template"),
            ("5", "Export Template"),
            ("b", "Back to Main Menu")
        ]
        
        for opt, desc in options:
            table.add_row(f"[{opt}]", desc)
            
        self.console.print(table)
        
        return Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "b"],
            show_choices=False
        )
        
    def display_settings_menu(self) -> Optional[str]:
        """Display settings menu."""
        self.console.clear()
        self.console.print(Panel("[bold cyan]Settings[/bold cyan]"))
        
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan")
        table.add_column("Description")
        
        options = [
            ("1", "Configure Data Directory"),
            ("2", "Configure Default Template"),
            ("3", "Configure Review Schedule"),
            ("4", "Configure Backup Settings"),
            ("5", "Configure UI Settings"),
            ("b", "Back to Main Menu")
        ]
        
        for opt, desc in options:
            table.add_row(f"[{opt}]", desc)
            
        self.console.print(table)
        
        return Prompt.ask(
            "\nSelect an option",
            choices=["1", "2", "3", "4", "5", "b"],
            show_choices=False
        ) 