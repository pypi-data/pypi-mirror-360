"""Main entry point for ENOUGH - A Mindful Journaling Tool."""
from pathlib import Path
from .cli.menu import Menu
from .config.settings import Settings
from .cli.interface import cli

def main():
    """Run the main program."""
    # Initialize settings
    settings = Settings()
    settings.setup_initial_config()
    
    # Initialize menu
    menu = Menu()
    
    while True:
        choice = menu.display_main_menu()
        
        if choice == "q":
            break
            
        elif choice == "1":  # Start Journaling
            template = menu.display_journal_menu()
            if template:
                cli(["start", template])
                
        elif choice == "2":  # Review
            option = menu.display_review_menu()
            if option != "b":
                cli(["review", option])
                
        elif choice == "3":  # Template Management
            option = menu.display_template_menu()
            if option != "b":
                cli(["template", option])
                
        elif choice == "4":  # Progress & Stats
            # TODO: Implement progress visualization
            pass
            
        elif choice == "5":  # Settings
            option = menu.display_settings_menu()
            if option != "b":
                cli(["settings", option])

if __name__ == "__main__":
    main() 