"""Configuration management for ENOUGH."""
import os
from pathlib import Path
import yaml
from typing import Dict, Any, Optional

class Settings:
    """Manages application settings and configuration."""
    
    def __init__(self):
        """Initialize settings manager."""
        self.app_dir = self._get_app_dir()
        self.config_file = self.app_dir / "config.yaml"
        self.default_config = {
            "data_dir": str(self.app_dir / "data"),
            "templates_dir": str(self.app_dir / "data" / "templates"),
            "submissions_dir": str(self.app_dir / "data" / "submissions"),
            "exercises_dir": str(self.app_dir / "data" / "exercises"),
            "default_template": "daily.yaml",
            "review_schedule": {
                "daily": True,
                "weekly": True,
                "monthly": True
            },
            "backup": {
                "enabled": True,
                "frequency": "daily",
                "keep_days": 30
            },
            "ui": {
                "theme": "default",
                "show_progress": True,
                "show_stats": True
            }
        }
        self.config = self._load_config()
        
    def _get_app_dir(self) -> Path:
        """Get the application data directory."""
        if os.name == 'nt':  # Windows
            app_dir = Path(os.getenv('APPDATA')) / "enough"
        else:  # Unix/Linux/MacOS
            app_dir = Path.home() / ".config" / "enough"
            
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if not self.config_file.exists():
            return self._create_default_config()
            
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)
            
    def _create_default_config(self) -> Dict[str, Any]:
        """Create and save default configuration."""
        # Create necessary directories
        for dir_key in ['data_dir', 'templates_dir', 'submissions_dir', 'exercises_dir']:
            Path(self.default_config[dir_key]).mkdir(parents=True, exist_ok=True)
            
        # Save default config
        with open(self.config_file, 'w') as f:
            yaml.dump(self.default_config, f)
            
        return self.default_config
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
        self._save_config()
        
    def _save_config(self) -> None:
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)
            
    def get_data_dir(self) -> Path:
        """Get the data directory path."""
        return Path(self.config['data_dir'])
        
    def get_templates_dir(self) -> Path:
        """Get the templates directory path."""
        return Path(self.config['templates_dir'])
        
    def get_submissions_dir(self) -> Path:
        """Get the submissions directory path."""
        return Path(self.config['submissions_dir'])
        
    def get_exercises_dir(self) -> Path:
        """Get the exercises directory path."""
        return Path(self.config['exercises_dir'])
        
    def migrate_data(self, old_dir: Path, new_dir: Path) -> None:
        """Migrate data from old directory to new directory."""
        if old_dir.exists():
            import shutil
            # Copy files
            if new_dir.exists():
                for item in old_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, new_dir)
                    else:
                        shutil.copytree(item, new_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copytree(old_dir, new_dir)
                
    def setup_initial_config(self) -> None:
        """Set up initial configuration and migrate data if needed."""
        # Check for data in old locations
        old_data_locations = [
            Path("Core/Data"),
            Path("Core/enough/data"),
            Path("%APPDATA%")  # This shouldn't be at root
        ]
        
        new_data_dir = self.get_data_dir()
        
        for old_loc in old_data_locations:
            if old_loc.exists():
                self.migrate_data(old_loc, new_data_dir)
                # Don't delete old data - let user do that manually if desired 